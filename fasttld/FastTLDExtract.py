#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Jophy and Wu Tingfeng
@file: psl.py

Copyright (c) 2022 Wu Tingfeng
Copyright (c) 2017-2018 Jophy
"""
import re
import socket
from collections import namedtuple

import idna

from fasttld.psl import getPublicSuffixList, update

# Characters valid in scheme names
SCHEME_RE = re.compile(r"(?i)^([a-z][a-z0-9+-.]*:)?[\\/]{2,}")

labelSeparators = "\u002e\u3002\uff0e\uff61"
labelSeparatorsSet = set(labelSeparators)
whitespace = " \t\n\v\f\r\uFEFF\u200b\u200c\u200d\u00a0\u1680\u0085\u0000"
endOfHostWithPortDelimiters = "/\\?#"
endOfHostWithPortDelimitersSet = set(endOfHostWithPortDelimiters)
endOfHostDelimitersSet = set(endOfHostWithPortDelimiters + ":")
invalidUserInfoCharsSet = set(endOfHostWithPortDelimiters + "[]")

IP_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])"
    r"[%s]){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$" % labelSeparators
)

TLDResult = namedtuple(
    "TLDResult",
    [
        "scheme",
        "userinfo",
        "subdomain",
        "domain",
        "suffix",
        "port",
        "path",
        "domain_name",
    ],
)


def replace_multiple(s, chars, replace_with):
    for char in chars:
        if char in s:
            s = s.replace(char, replace_with)
    return s


def is_ipv6(maybe_ipv6):
    try:
        socket.inet_pton(socket.AF_INET6, replace_multiple(maybe_ipv6, labelSeparators, "."))
        return True
    except Exception:
        pass
    return False


def looks_like_ip(maybe_ip):
    """Does the given str look like an IP address?"""
    return IP_RE.match(maybe_ip)


def check_numeric(maybe_numeric):
    try:
        int(maybe_numeric)
    except ValueError:
        return False
    return True


def index_last_char_before(s, b, not_after_chars):
    """index_last_char_before returns the index of the last instance of char b
    before any char in not_after_chars, otherwise -1
    """
    idx = -1
    for i, c in enumerate(s):
        if c in not_after_chars:
            break
        if c == b:
            idx = i
    return idx


def index_any(s, charset):
    for i, c in enumerate(s):
        if c in charset:
            return i
    return -1


def last_index_any(s, charset):
    for i, c in enumerate(reversed(s), start=1):
        if c in charset:
            return len(s) - i
    return -1


class FastTLDExtract(object):
    def __init__(self, exclude_private_suffix=False, file_path=""):
        self.trie = self._trie_construct(exclude_private_suffix, file_path)

    def update(self, *args, **kwargs):
        update(*args, **kwargs)

    def nested_dict(self, dic, keys):
        """
        The idea of this function is based on https://stackoverflow.com/questions/13687924
        :param dic:
        :param keys:
        :return:
        """
        end = False
        for key in keys[:-1]:
            dic_bk = dic
            if key not in dic:
                dic[key] = {}
            dic = dic[key]
            if isinstance(dic, bool):
                end = True
                dic = dic_bk
                dic[keys[-2]] = {"_END": True, keys[-1]: True}
        if not end:
            dic[keys[-1]] = True

    def _trie_construct(self, exclude_private_suffix, file_path=""):
        """
        This function for building a trie structure based on Mozilla Public Suffix List.
        In order to construct this, all suffixes sorted in a reverse order.
        For example, www.google.com -> com.google.www
        :return: a trie dict
        """
        tld_trie = {}
        PublicSuffixList, PrivateSuffixList, AllSuffixList = getPublicSuffixList(file_path)
        SuffixList = PublicSuffixList if exclude_private_suffix else AllSuffixList
        for suffix in SuffixList:
            if "." in suffix:
                sp = suffix.split(".")
                sp.reverse()
                self.nested_dict(tld_trie, sp)
            else:
                tld_trie[suffix] = {"_END": True}
        for key, val in tld_trie.items():
            if len(val) == 1 and "_END" in val:
                tld_trie[key] = True
        return tld_trie

    def __call__(self, *args, **kwargs):
        return self.extract(*args, **kwargs)

    def extract(self, raw_url, subdomain=True, format=False):
        """
        Extract suffix and subdomain from a Domain.
        :param raw_url:
        :param subdomain: Output options. This option will reduce efficiency. Maybe 10%
        :param format: To format raw_url string.
        :return: NamedTuple(scheme, userinfo, subdomain, domain, suffix, port, path, domain_name)
        >>> FastTLDExtract.extract('www.google.com.hk', subdomain=True)
        >>> TLDResult(scheme='', userinfo='', subdomain='www', domain='google', suffix='com.hk', port='', path='', domain_name='google.com.hk')

        >>> FastTLDExtract.extract('127.0.0.1', subdomain=True)
        >>> TLDResult(scheme='', userinfo='', subdomain='', domain='127.0.0.1', suffix='', port='', path='', domain_name='127.0.0.1')
        """

        def urlParts():
            return TLDResult(
                        ret_scheme,
                        ret_userinfo,
                        ret_subdomain,
                        ret_domain,
                        ret_suffix,
                        ret_port,
                        ret_path,
                        ret_domain_name,
                    )

        ret_scheme = ret_userinfo = ret_subdomain = ret_domain = ""
        ret_suffix = ret_port = ret_path = ret_domain_name = ""

        # Extract URL scheme
        netloc_with_scheme = raw_url.strip(whitespace)
        netloc = SCHEME_RE.sub("", netloc_with_scheme)
        ret_scheme = netloc_with_scheme[:len(netloc_with_scheme)-len(netloc)]

        # Extract URL userinfo
        at_idx = index_last_char_before(netloc, "@", invalidUserInfoCharsSet)
        if at_idx != -1:
            ret_userinfo = netloc[:at_idx]
            netloc = netloc[at_idx+1:]

        # Find square brackets (if any) and host end index
        openingSquareBracketIdx = closingSquareBracketIdx = hostEndIdx = -1
        for i, r in enumerate(netloc):
            if r == "[":
                # Check for opening square bracket
                if i > 0:
                    # Reject if opening square bracket is not first character of netloc
                    return urlParts()
                openingSquareBracketIdx = i
            if r == "]":
                # Check for closing square bracket
                closingSquareBracketIdx = i

            if openingSquareBracketIdx == -1:
                if closingSquareBracketIdx != -1:
                    # Reject if closing square bracket present but no opening square bracket
                    return urlParts()
                if r in endOfHostDelimitersSet:
                    # If no square brackets
                    # Check for endOfHostDelimitersSet
                    hostEndIdx = i

            if openingSquareBracketIdx != -1 and closingSquareBracketIdx != -1:
                if (closingSquareBracketIdx > openingSquareBracketIdx and
                   r in endOfHostWithPortDelimitersSet):
                    # If opening + closing square bracket are present in correct order
                    # check for endOfHostWithPortDelimitersSet
                    hostEndIdx = i
            if hostEndIdx != -1:
                break
            if i == len(netloc) - 1 and closingSquareBracketIdx < openingSquareBracketIdx:
                # Reject if end of netloc reached but incomplete square bracket pair
                return urlParts()

        if closingSquareBracketIdx == len(netloc) - 1:
            hostEndIdx = -1
        elif closingSquareBracketIdx != -1:
            hostEndIdx = closingSquareBracketIdx + 1

        # Check for IPv6 address
        if closingSquareBracketIdx > openingSquareBracketIdx:
            if not is_ipv6(netloc[1:closingSquareBracketIdx]):
                # Have square brackets but invalid IPv6 => Domain is invalid
                return urlParts()
            # Closing square bracket in correct place and IPv6 is valid
            ret_domain = netloc[1:closingSquareBracketIdx]
            ret_domain_name = netloc[1:closingSquareBracketIdx]

        after_host = ""
        # Separate URL host from subcomponents thereafter
        if hostEndIdx != -1:
            after_host = netloc[hostEndIdx:]
            netloc = netloc[0:hostEndIdx]

        invalid_punycode = False
        try:
            puny_netloc = self.format(netloc)
        except Exception:
            puny_netloc = ""
            invalid_punycode = True
        if format:
            netloc = puny_netloc

        # Extract Port and "Path" if any
        if len(after_host):
            path_start_index = index_any(after_host, endOfHostWithPortDelimitersSet)
            invalid_port = False
            if after_host[0] == ':':
                if path_start_index == -1:
                    maybe_port = after_host[1:]
                else:
                    maybe_port = after_host[1:path_start_index]
                if not(check_numeric(maybe_port) and 0 <= int(maybe_port) <= 65535):
                    invalid_port = True
                else:
                    ret_port = maybe_port
            if not invalid_port and path_start_index != -1 and path_start_index != len(after_host):
                # If there is any path/query/fragment after the URL authority component...
                ret_path = after_host[path_start_index:]

        if closingSquareBracketIdx > 0:
            # Is IPv6 address
            return urlParts()

        # Check for IPv4 address
        if looks_like_ip(netloc):
            ret_domain = ret_domain_name = netloc
            return urlParts()

        # host is invalid if host cannot be converted to unicode
        if invalid_punycode:
            return urlParts()

        # Define the root node
        node = self.trie

        hasSuffix = end = False
        previousSepIdx = 0
        sepIdx = len(netloc)

        while not end:
            label = ""
            previousSepIdx = sepIdx
            sepIdx = last_index_any(netloc[0:sepIdx], labelSeparatorsSet)
            if sepIdx != -1:
                label = netloc[sepIdx+1: previousSepIdx]
            else:
                label = netloc[0:previousSepIdx]
                end = True

            if "*" in node:
                # check if label falls under any wildcard exception rule
                # e.g. !www.ck
                if ("!%s" % label) in node:
                    sepIdx = previousSepIdx
                break

            # check if label is part of a TLD
            if label in node:
                hasSuffix = True
                node = node[label]
                if node is True:
                    # label is at a leaf node (no children) ; break out of loop
                    break
            else:
                if previousSepIdx != len(netloc):
                    sepIdx = previousSepIdx
                break

        if sepIdx == -1:
            sepIdx = len(netloc)

        if hasSuffix:
            if sepIdx < len(netloc):  # If there is a Domain
                ret_suffix = netloc[sepIdx+1:]
                domainStartSepIdx = last_index_any(netloc[0:sepIdx], labelSeparatorsSet)
                if domainStartSepIdx != -1:  # If there is a SubDomain
                    domainStartIdx = domainStartSepIdx + 1
                    ret_domain = netloc[domainStartIdx:sepIdx]
                    ret_domain_name = netloc[domainStartIdx:]
                    if subdomain:  # If SubDomain is to be included
                        ret_subdomain = netloc[0:domainStartSepIdx]
                else:
                    ret_domain = netloc[domainStartSepIdx+1: sepIdx]
                    ret_domain_name = netloc[domainStartSepIdx+1:]
            else:
                # If only Suffix exists
                ret_suffix = netloc

        elif sepIdx < len(netloc):  # If there is a SubDomain
            domainStartSepIdx = last_index_any(netloc, labelSeparatorsSet)
            domainStartIdx = domainStartSepIdx + 1
            ret_domain = netloc[domainStartIdx:]
            if subdomain:  # If SubDomain is to be included
                ret_subdomain = netloc[0:domainStartSepIdx]
        else:  # If there is no SubDomain
            ret_domain = netloc

        return urlParts()

    def format(self, raw_url):
        """
        Convert to punycode
        """
        return idna.encode(raw_url).decode()
