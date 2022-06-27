# -*- coding: utf-8 -*-
import unittest

from fasttld import FastTLDExtract

all_suffix = FastTLDExtract(exclude_private_suffix=False)
no_private_suffix = FastTLDExtract(exclude_private_suffix=True)


class FastTLDTrieCase(unittest.TestCase):
    def test_all_suffix_trie(self):
        trie = all_suffix.trie
        self.assertEqual(trie["cn"]["com"], True)
        self.assertEqual("blogspot" in trie["uk"]["co"], True)
        self.assertEqual("*" in trie["uk"], False)
        self.assertEqual("_END" in trie["cn"], True)
        self.assertEqual(trie["ck"]["*"], True)
        self.assertEqual(trie["ck"]["!www"], True)
        self.assertEqual(trie["ir"]["xn--mgba3a4f16a"], True)
        # private domain test
        self.assertEqual(trie["com"]["appspot"], True)
        self.assertEqual(trie["ee"]["com"]["blogspot"], True)
        self.assertEqual(trie["com"]["0emm"]["*"], True)

    def test_idn_suffix_trie(self):
        trie = all_suffix.trie
        self.assertEqual(trie["香港"]["公司"], True)
        self.assertEqual(trie["新加坡"], True)

    def test_no_private_domain_trie(self):
        trie = no_private_suffix.trie
        self.assertEqual(trie["cn"]["com"], True)
        self.assertEqual(trie["uk"]["co"], True)
        # private domain test
        self.assertEqual(trie["com"], True)  # *.0emm.com or the domains like hk.com, cn.com ,etc.
        self.assertEqual("no-ip.biz" in trie, False)
        self.assertEqual("github" in trie["io"], False)

    def test_nested_dict(self):
        d = {}
        all_suffix.nested_dict(d, keys=["ac"])
        all_suffix.nested_dict(d, keys=["ac", "com"])
        all_suffix.nested_dict(d, keys=["ac", "edu"])
        all_suffix.nested_dict(d, keys=["ac", "gov"])
        all_suffix.nested_dict(d, keys=["ac", "net"])
        all_suffix.nested_dict(d, keys=["ac", "mil"])
        all_suffix.nested_dict(d, keys=["ac", "org"])

        all_suffix.nested_dict(d, keys=["ck", "*"])
        all_suffix.nested_dict(d, keys=["ck", "!www"])
        self.assertDictEqual(
            d,
            {
                "ac": {
                    "_END": True,
                    "com": True,
                    "edu": True,
                    "gov": True,
                    "net": True,
                    "mil": True,
                    "org": True,
                },
                "ck": {"*": True, "!www": True},
            },
        )


schemeTests = [
    {
        "urlParams": {"URL": "h://example.com"},
        "expected": {
            "Scheme": "h://",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "Single character Scheme",
    },
    {
        "urlParams": {"URL": "hTtPs://example.com"},
        "expected": {
            "Scheme": "hTtPs://",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "Capitalised Scheme",
    },
    {
        "urlParams": {"URL": "git-ssh://example.com"},
        "expected": {
            "Scheme": "git-ssh://",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "Scheme with -",
    },
    {
        "urlParams": {
            "URL": "https://username:password@foo.example.com:999/some/path?param1=value1&param2=葡萄"
        },
        "expected": {
            "Scheme": "https://",
            "UserInfo": "username:password",
            "SubDomain": "foo",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Port": "999",
            "Path": "/some/path?param1=value1&param2=葡萄",
        },
        "description": "Full https URL with SubDomain",
    },
    {
        "urlParams": {"URL": "http://www.example.com"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "www",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "Full http URL with SubDomain no path",
    },
    {
        "urlParams": {
            "URL": "http://example.co.uk/path?param1=value1&param2=葡萄&param3=value3&param4=value4&src=https%3A%2F%2Fwww.example.net%2F"
        },
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "co.uk",
            "RegisteredDomain": "example.co.uk",
            "Path": "/path?param1=value1&param2=葡萄&param3=value3&param4=value4&src=https%3A%2F%2Fwww.example.net%2F",
        },
        "description": "Full http URL with no SubDomain",
    },
    {
        "urlParams": {
            "URL": "http://big.long.sub.domain.example.co.uk/path?param1=value1&param2=葡萄&param3=value3&param4=value4&src=https%3A%2F%2Fwww.example.net%2F"
        },
        "expected": {
            "Scheme": "http://",
            "SubDomain": "big.long.sub.domain",
            "Domain": "example",
            "Suffix": "co.uk",
            "RegisteredDomain": "example.co.uk",
            "Path": "/path?param1=value1&param2=葡萄&param3=value3&param4=value4&src=https%3A%2F%2Fwww.example.net%2F",
        },
        "description": "Full http URL with SubDomain",
    },
    {
        "urlParams": {
            "URL": "ftp://username名字:password@mail.example.co.uk:666/path?param1=value1&param2=葡萄&param3=value3&param4=value4&src=https%3A%2F%2Fwww.example.net%2F"
        },
        "expected": {
            "Scheme": "ftp://",
            "UserInfo": "username名字:password",
            "SubDomain": "mail",
            "Domain": "example",
            "Suffix": "co.uk",
            "RegisteredDomain": "example.co.uk",
            "Port": "666",
            "Path": "/path?param1=value1&param2=葡萄&param3=value3&param4=value4&src=https%3A%2F%2Fwww.example.net%2F",
        },
        "description": "Full ftp URL with SubDomain",
    },
    {
        "urlParams": {"URL": "git+ssh://www.example.com/"},
        "expected": {
            "Scheme": "git+ssh://",
            "SubDomain": "www",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Path": "/",
        },
        "description": "Full git+ssh URL with SubDomain",
    },
    {
        "urlParams": {"URL": "ssh://server.example.com/"},
        "expected": {
            "Scheme": "ssh://",
            "SubDomain": "server",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Path": "/",
        },
        "description": "Full ssh URL with SubDomain",
    },
    {
        "urlParams": {"URL": "http://www.www.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "www",
            "Domain": "www",
            "Suffix": "net",
            "RegisteredDomain": "www.net",
        },
        "description": "Multiple www",
    },
]
noSchemeTests = [
    {
        "urlParams": {"URL": "localhost"},
        "expected": {"Domain": "localhost"},
        "description": "localhost",
    },
    {
        "urlParams": {"URL": "org"},
        "expected": {"Suffix": "org"},
        "description": "Single TLD | Suffix Only",
    },
    {
        "urlParams": {"URL": "co.th"},
        "expected": {"Suffix": "co.th"},
        "description": "Double TLD | Suffix Only",
    },
    {
        "urlParams": {"URL": "users@example.com"},
        "expected": {
            "UserInfo": "users",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "UserInfo + Domain | No Scheme",
    },
    {
        "urlParams": {"URL": "mailto:users@example.com"},
        "expected": {
            "UserInfo": "mailto:users",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "Mailto | No Scheme",
    },
    {
        "urlParams": {"URL": "example.com:999"},
        "expected": {
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Port": "999",
        },
        "description": "Domain + Port | No Scheme",
    },
    {
        "urlParams": {"URL": "example.com"},
        "expected": {"Domain": "example", "Suffix": "com", "RegisteredDomain": "example.com"},
        "description": "Domain | No Scheme",
    },
    {
        "urlParams": {"URL": "255.255.example.com"},
        "expected": {
            "SubDomain": "255.255",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "Numeric SubDomain + Domain | No Scheme",
    },
    {
        "urlParams": {"URL": "server.example.com/path"},
        "expected": {
            "SubDomain": "server",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Path": "/path",
        },
        "description": "SubDomain, Domain and Path | No Scheme",
    },
]
userInfoTests = [
    {
        "urlParams": {"URL": "https://username@example.com"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": "username",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "username",
    },
    {
        "urlParams": {"URL": "https://password@example.com"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": "password",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "username + password",
    },
    {
        "urlParams": {"URL": "https://:password@example.com"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": ":password",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "colon but empty username",
    },
    {
        "urlParams": {"URL": "https://username:@example.com"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": "username:",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "colon but empty password",
    },
    {
        "urlParams": {"URL": "https://usern@me:password@example.com"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": "usern@me:password",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "@ in username",
    },
    {
        "urlParams": {"URL": "https://usern@me:p@ssword@example.com"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": "usern@me:p@ssword",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "@ in password",
    },
    {
        "urlParams": {"URL": "https://usern@me:@example.com"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": "usern@me:",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "colon but empty password; @ in username",
    },
    {
        "urlParams": {"URL": "https://:p@ssword@example.com"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": ":p@ssword",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
        },
        "description": "colon but empty username; @ in password",
    },
    {
        "urlParams": {"URL": "https://usern@m%40e:password@example.com/p@th?q=@go"},
        "expected": {
            "Scheme": "https://",
            "UserInfo": "usern@m%40e:password",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Path": "/p@th?q=@go",
        },
        "description": "@ in UserInfo and Path",
    },
]
ipv4Tests = [
    {
        "urlParams": {"URL": "127.0.0.1"},
        "expected": {"Domain": "127.0.0.1", "RegisteredDomain": "127.0.0.1"},
        "description": "Basic IPv4 Address",
    },
    {
        "urlParams": {"URL": "http://127.0.0.1:5000"},
        "expected": {
            "Scheme": "http://",
            "Domain": "127.0.0.1",
            "RegisteredDomain": "127.0.0.1",
            "Port": "5000",
        },
        "description": "Basic IPv4 Address with Scheme and Port",
    },
    {
        "urlParams": {"URL": "127\uff0e0\u30020\uff611"},
        "expected": {
            "Domain": "127\uff0e0\u30020\uff611",
            "RegisteredDomain": "127\uff0e0\u30020\uff611",
        },
        "description": "Basic IPv4 Address | Internationalised label separators",
    },
    {
        "urlParams": {"URL": "http://127\uff0e0\u30020\uff611:5000"},
        "expected": {
            "Scheme": "http://",
            "Domain": "127\uff0e0\u30020\uff611",
            "Port": "5000",
            "RegisteredDomain": "127\uff0e0\u30020\uff611",
        },
        "description": "Basic IPv4 Address with Scheme and Port | Internationalised label separators",
    },
]
ipv6Tests = [
    {
        "urlParams": {"URL": "[aBcD:ef01:2345:6789:aBcD:ef01:2345:6789]"},
        "expected": {
            "Domain": "aBcD:ef01:2345:6789:aBcD:ef01:2345:6789",
            "RegisteredDomain": "aBcD:ef01:2345:6789:aBcD:ef01:2345:6789",
        },
        "description": "Basic IPv6 Address",
    },
    {
        "urlParams": {"URL": "http://[aBcD:ef01:2345:6789:aBcD:ef01:2345:6789]:5000"},
        "expected": {
            "Scheme": "http://",
            "Domain": "aBcD:ef01:2345:6789:aBcD:ef01:2345:6789",
            "RegisteredDomain": "aBcD:ef01:2345:6789:aBcD:ef01:2345:6789",
            "Port": "5000",
        },
        "description": "Basic IPv6 Address with Scheme and Port",
    },
    {
        "urlParams": {"URL": "http://[aBcD:ef01:2345:6789:aBcD:ef01:127.0.0.1]:5000"},
        "expected": {
            "Scheme": "http://",
            "Domain": "aBcD:ef01:2345:6789:aBcD:ef01:127.0.0.1",
            "RegisteredDomain": "aBcD:ef01:2345:6789:aBcD:ef01:127.0.0.1",
            "Port": "5000",
        },
        "description": "Basic IPv6 Address + trailing IPv4 address with Scheme and Port",
    },
    {
        "urlParams": {
            "URL": "http://[aBcD:ef01:2345:6789:aBcD:ef01:127\uff0e0\u30020\uff611]:5000"
        },
        "expected": {
            "Scheme": "http://",
            "Domain": "aBcD:ef01:2345:6789:aBcD:ef01:127\uff0e0\u30020\uff611",
            "RegisteredDomain": "aBcD:ef01:2345:6789:aBcD:ef01:127\uff0e0\u30020\uff611",
            "Port": "5000",
        },
        "description": "Basic IPv6 Address + trailing IPv4 address with Scheme and Port | Internationalised label separators",
    },
    {
        "urlParams": {"URL": "http://[::2345:6789:aBcD:ef01:2345:678]:5000"},
        "expected": {
            "Scheme": "http://",
            "Domain": "::2345:6789:aBcD:ef01:2345:678",
            "RegisteredDomain": "::2345:6789:aBcD:ef01:2345:678",
            "Port": "5000",
        },
        "description": "Basic IPv6 Address with Scheme and Port | have leading ellipsis",
    },
    {
        "urlParams": {"URL": "http://[::]:5000"},
        "expected": {"Scheme": "http://", "Domain": "::", "RegisteredDomain": "::", "Port": "5000"},
        "description": "Basic IPv6 Address with Scheme and Port | only ellipsis",
    },
    {
        "urlParams": {"URL": "http://[aBcD:ef01:2345:6789:aBcD:ef01::]:5000"},
        "expected": {
            "Scheme": "http://",
            "Domain": "aBcD:ef01:2345:6789:aBcD:ef01::",
            "RegisteredDomain": "aBcD:ef01:2345:6789:aBcD:ef01::",
            "Port": "5000",
        },
        "description": "Basic IPv6 Address with Scheme and Port and bad IP | even number of empty hextets",
    },
]
ignoreSubDomainsTests = [
    {
        "urlParams": {"URL": "maps.google.com.sg", "IgnoreSubDomains": True},
        "expected": {
            "Domain": "google",
            "Suffix": "com.sg",
            "RegisteredDomain": "google.com.sg",
        },
        "description": "Ignore SubDomain",
    },
]
privateSuffixTests = [
    {
        "includePrivateSuffix": True,
        "urlParams": {"URL": "https://brb.i.am.going.to.be.blogspot.com:5000/a/b/c/d.txt?id=42"},
        "expected": {
            "Scheme": "https://",
            "SubDomain": "brb.i.am.going.to",
            "Domain": "be",
            "Suffix": "blogspot.com",
            "RegisteredDomain": "be.blogspot.com",
            "Port": "5000",
            "Path": "/a/b/c/d.txt?id=42",
        },
        "description": "Include Private Suffix",
    },
    {
        "includePrivateSuffix": True,
        "urlParams": {"URL": "global.prod.fastly.net"},
        "expected": {
            "Suffix": "global.prod.fastly.net",
        },
        "description": "Include Private Suffix | Suffix only",
    },
]
periodsAndWhiteSpacesTests = [
    {
        "urlParams": {
            "URL": "https://brb\u002ei\u3002am\uff0egoing\uff61to\uff0ebe\u3002a\uff61fk"
        },
        "expected": {
            "Scheme": "https://",
            "SubDomain": "brb\u002ei\u3002am\uff0egoing\uff61to",
            "Domain": "be",
            "Suffix": "a\uff61fk",
            "RegisteredDomain": "be\u3002a\uff61fk",
        },
        "description": "Internationalised label separators",
    },
    {
        "urlParams": {"URL": "a\uff61fk"},
        "expected": {"Suffix": "a\uff61fk"},
        "description": "Internationalised label separators | Suffix only",
    },
    {
        "urlParams": {
            "URL": " https://brb\u002ei\u3002am\uff0egoing\uff61to\uff0ebe\u3002a\uff61fk/a/b/c. \uff61 "
        },
        "expected": {
            "Scheme": "https://",
            "SubDomain": "brb\u002ei\u3002am\uff0egoing\uff61to",
            "Domain": "be",
            "Suffix": "a\uff61fk",
            "RegisteredDomain": "be\u3002a\uff61fk",
            "Path": "/a/b/c. \uff61",
        },
        "description": "Surrounded by extra whitespace",
    },
    {
        "urlParams": {
            "URL": " https://brb\u002ei\u3002am\uff0egoing\uff61to\uff0ebe\u3002a\uff61fk/a/B/c. \uff61 ",
            "ConvertURLToPunyCode": True,
        },
        "expected": {
            "Scheme": "https://",
            "SubDomain": "brb.i.am.going.to",
            "Domain": "be",
            "Suffix": "a.fk",
            "RegisteredDomain": "be.a.fk",
            "Path": "/a/B/c. \uff61",
        },
        "description": "Surrounded by extra whitespace | PunyCode",
    },
    {
        "urlParams": {"URL": "http://1.1.1.1 &@2.2.2.2:33/4.4.4.4?1.1.1.1# @3.3.3.3/"},
        "expected": {
            "Scheme": "http://",
            "UserInfo": "1.1.1.1 &",
            "Domain": "2.2.2.2",
            "RegisteredDomain": "2.2.2.2",
            "Port": "33",
            "Path": "/4.4.4.4?1.1.1.1# @3.3.3.3/",
        },
        "description": "Whitespace in UserInfo",
    },
]
invalidTests = [
    {"urlParams": {}, "expected": {}, "description": "empty string"},
    {
        "urlParams": {"URL": "https://"},
        "expected": {"Scheme": "https://"},
        "description": "Scheme only",
    },
    {
        "urlParams": {"URL": "1b://example.com"},
        "expected": {"Domain": "1b"},
        "description": "Scheme beginning with non-alphabet",
    },
    {
        "urlParams": {"URL": "maps.google.com.sg:8589934592/this/path/will/not/be/parsed"},
        "expected": {
            "SubDomain": "maps",
            "Domain": "google",
            "Suffix": "com.sg",
            "RegisteredDomain": "google.com.sg",
        },
        "description": "Invalid Port number",
    },
    {
        "urlParams": {"URL": "//server.example.com/path"},
        "expected": {
            "Scheme": "//",
            "SubDomain": "server",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Path": "/path",
        },
        "description": "Double-slash only Scheme with subdomain",
    },
    {
        "urlParams": {"URL": "http://temasek"},
        "expected": {"Scheme": "http://", "Suffix": "temasek"},
        "description": "Basic URL with TLD only",
    },
    {
        "urlParams": {"URL": "http://temasek.this-tld-cannot-be-real"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "temasek",
            "Domain": "this-tld-cannot-be-real",
        },
        "description": "Basic URL with bad TLD",
    },
    {
        "urlParams": {"URL": "http://temasek.temasek.this-tld-cannot-be-real"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "temasek.temasek",
            "Domain": "this-tld-cannot-be-real",
        },
        "description": "Basic URL with subdomain and bad TLD",
    },
    {
        "urlParams": {"URL": "http://127.0.0.256"},
        "expected": {"Scheme": "http://", "SubDomain": "127.0.0", "Domain": "256"},
        "description": "Basic IPv4 Address URL with bad IP",
    },
    {
        "urlParams": {"URL": "http://127\uff0e0\u30020\uff61256:5000"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "127\uff0e0\u30020",
            "Port": "5000",
            "Domain": "256",
        },
        "description": "Basic IPv4 Address with Scheme and Port and bad IP | Internationalised label separators",
    },
    {
        "urlParams": {"URL": "http://192.168.01.1:5000"},
        "expected": {"Scheme": "http://", "SubDomain": "192.168.01", "Domain": "1", "Port": "5000"},
        "description": "Basic IPv4 Address with Scheme and Port and bad IP | octet with leading zero",
    },
    {
        "urlParams": {"URL": "http://a:b@xn--tub-1m9d15sfkkhsifsbqygyujjrw60.com"},
        "expected": {"Scheme": "http://", "UserInfo": "a:b"},
        "description": "Invalid punycode Domain",
    },
    {
        "urlParams": {"URL": "http://[aBcD:ef01:2345:6789:aBcD:ef01:2345:6789:5000"},
        "expected": {"Scheme": "http://"},
        "description": "Basic IPv6 Address with Scheme and Port with no closing bracket",
    },
    {
        "urlParams": {"URL": "http://[aBcD:ef01:2345:6789:aBcD:::]:5000"},
        "expected": {"Scheme": "http://"},
        "description": "Basic IPv6 Address with Scheme and Port and bad IP | odd number of empty hextets",
    },
    {
        "urlParams": {"URL": "http://[aBcD:ef01:2345:6789:aBcD:ef01:2345:fffffffffffffffff]:5000"},
        "expected": {"Scheme": "http://"},
        "description": "Basic IPv6 Address with Scheme and Port and bad IP | hextet too big",
    },
    {
        "urlParams": {
            "URL": "http://[aBcD:ef01:2345:6789:aBcD:ef01:127\uff0e256\u30020\uff611]:5000"
        },
        "expected": {"Scheme": "http://"},
        "description": "Basic IPv6 Address + trailing IPv4 address with Scheme and Port and bad IPv4 | Internationalised label separators",
    },
    {
        "urlParams": {"URL": "http://["},
        "expected": {"Scheme": "http://"},
        "description": "Single opening square bracket",
    },
    {
        "urlParams": {"URL": "http://a["},
        "expected": {"Scheme": "http://"},
        "description": "Single opening square bracket after alphabet",
    },
    {
        "urlParams": {"URL": "http://]"},
        "expected": {"Scheme": "http://"},
        "description": "Single closing square bracket",
    },
    {
        "urlParams": {"URL": "http://a]"},
        "expected": {"Scheme": "http://"},
        "description": "Single closing square bracket after alphabet",
    },
    {
        "urlParams": {"URL": "http://]["},
        "expected": {"Scheme": "http://"},
        "description": "closing square bracket before opening square bracket",
    },
    {
        "urlParams": {"URL": "http://a]["},
        "expected": {"Scheme": "http://"},
        "description": "closing square bracket before opening square bracket after alphabet",
    },
    {
        "urlParams": {"URL": "http://[]"},
        "expected": {"Scheme": "http://"},
        "description": "Empty pair of square brackets",
    },
    {
        "urlParams": {"URL": "http://a[]"},
        "expected": {"Scheme": "http://"},
        "description": "Empty pair of square brackets after alphabet",
    },
    {
        "urlParams": {"URL": "http://a[127.0.0.1]"},
        "expected": {"Scheme": "http://"},
        "description": "IPv4 in square brackets after alphabet",
    },
    {
        "urlParams": {"URL": "http://a[aBcD:ef01:2345:6789:aBcD:ef01:127\uff0e255\u30020\uff611]"},
        "expected": {"Scheme": "http://"},
        "description": "IPv6 in square brackets after alphabet",
    },
    {
        "urlParams": {"URL": "http://[127.0.0.1]"},
        "expected": {"Scheme": "http://"},
        "description": "IPv4 in square brackets",
    },
    # Test cases from net/ip-test.go
    {
        "urlParams": {"URL": "http://[-0.0.0.0]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[0.-1.0.0]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[0.0.-2.0]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[0.0.0.-3]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[127.0.0.256]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[abc]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[123:]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[fe80::1%lo0]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[fe80::1%911]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[a1:a2:a3:a4::b1:b2:b3:b4]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[127.001.002.003]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[::ffff:127.001.002.003]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[123.000.000.000]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[1.2..4]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    {
        "urlParams": {"URL": "http://[0123.0.0.1]"},
        "expected": {"Scheme": "http://"},
        "description": "net/ip-test.go",
    },
    # {"urlParams": {"URL": "git+ssh://www.!example.com/"}, "expected": {}, "description": "Full git+ssh URL with bad Domain"},
]
internationalTLDTests = [
    {
        "urlParams": {"URL": "http://example.敎育.hk/地图/A/b/C?编号=42", "ConvertURLToPunyCode": True},
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "xn--lcvr32d.hk",
            "RegisteredDomain": "example.xn--lcvr32d.hk",
            "Path": "/地图/A/b/C?编号=42",
        },
        "description": "Basic URL with mixed international TLD (result in punycode)",
    },
    {
        "urlParams": {"URL": "http://example.обр.срб/地图/A/b/C?编号=42", "ConvertURLToPunyCode": True},
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "xn--90azh.xn--90a3ac",
            "RegisteredDomain": "example.xn--90azh.xn--90a3ac",
            "Path": "/地图/A/b/C?编号=42",
        },
        "description": "Basic URL with full international TLD (result in punycode)",
    },
    {
        "urlParams": {"URL": "http://example.敎育.hk/地图/A/b/C?编号=42"},
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "敎育.hk",
            "RegisteredDomain": "example.敎育.hk",
            "Path": "/地图/A/b/C?编号=42",
        },
        "description": "Basic URL with mixed international TLD (result in unicode)",
    },
    {
        "urlParams": {"URL": "http://example.обр.срб/地图/A/b/C?编号=42"},
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "обр.срб",
            "RegisteredDomain": "example.обр.срб",
            "Path": "/地图/A/b/C?编号=42",
        },
        "description": "Basic URL with full international TLD (result in unicode)",
    },
    {
        "urlParams": {
            "URL": "http://example.xn--ciqpn.hk/地图/A/b/C?编号=42",
            "ConvertURLToPunyCode": True,
        },
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "xn--ciqpn.hk",
            "RegisteredDomain": "example.xn--ciqpn.hk",
            "Path": "/地图/A/b/C?编号=42",
        },
        "description": "Basic URL with mixed punycode international TLD (result in punycode)",
    },
    {
        "urlParams": {
            "URL": "http://example.xn--90azh.xn--90a3ac/地图/A/b/C?编号=42",
            "ConvertURLToPunyCode": True,
        },
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "xn--90azh.xn--90a3ac",
            "RegisteredDomain": "example.xn--90azh.xn--90a3ac",
            "Path": "/地图/A/b/C?编号=42",
        },
        "description": "Basic URL with full punycode international TLD (result in punycode)",
    },
    {
        "urlParams": {"URL": "http://example.xn--ciqpn.hk"},
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "xn--ciqpn.hk",
            "RegisteredDomain": "example.xn--ciqpn.hk",
        },
        "description": "Basic URL with mixed punycode international TLD (no further conversion to punycode)",
    },
    {
        "urlParams": {"URL": "http://example.xn--90azh.xn--90a3ac"},
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "xn--90azh.xn--90a3ac",
            "RegisteredDomain": "example.xn--90azh.xn--90a3ac",
        },
        "description": "Basic URL with full punycode international TLD (no further conversion to punycode)",
    },
    {
        "urlParams": {"URL": "http://xN--h1alffa9f.xn--90azh.xn--90a3ac"},
        "expected": {
            "Scheme": "http://",
            "Domain": "xN--h1alffa9f",
            "Suffix": "xn--90azh.xn--90a3ac",
            "RegisteredDomain": "xN--h1alffa9f.xn--90azh.xn--90a3ac",
        },
        "description": "Mixed case Punycode Domain with full punycode international TLD (no further conversion to punycode)",
    },
    {
        "urlParams": {
            "URL": "http://xN--h1alffa9f.xn--90azh.xn--90a3ac",
            "ConvertURLToPunyCode": True,
        },
        "expected": {
            "Scheme": "http://",
            "Domain": "xN--h1alffa9f",
            "Suffix": "xn--90azh.xn--90a3ac",
            "RegisteredDomain": "xN--h1alffa9f.xn--90azh.xn--90a3ac",
        },
        "description": "Mixed case Punycode Domain with full punycode international TLD (with further conversion to punycode)",
    },
]
domainOnlySingleTLDTests = [
    {
        "urlParams": {"URL": "https://example.ai/en"},
        "expected": {
            "Scheme": "https://",
            "Domain": "example",
            "Suffix": "ai",
            "RegisteredDomain": "example.ai",
            "Path": "/en",
        },
        "description": "Domain only + ai",
    },
    {
        "urlParams": {"URL": "https://example.co/en"},
        "expected": {
            "Scheme": "https://",
            "Domain": "example",
            "Suffix": "co",
            "RegisteredDomain": "example.co",
            "Path": "/en",
        },
        "description": "Domain only + co",
    },
    {
        "urlParams": {"URL": "https://example.sg/en"},
        "expected": {
            "Scheme": "https://",
            "Domain": "example",
            "Suffix": "sg",
            "RegisteredDomain": "example.sg",
            "Path": "/en",
        },
        "description": "Domain only + sg",
    },
    {
        "urlParams": {"URL": "https://example.tv/en"},
        "expected": {
            "Scheme": "https://",
            "Domain": "example",
            "Suffix": "tv",
            "RegisteredDomain": "example.tv",
            "Path": "/en",
        },
        "description": "Domain only + tv",
    },
]
pathTests = [
    {
        "urlParams": {"URL": "http://www.example.com/this:that"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "www",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Path": "/this:that",
        },
        "description": "Colon in Path",
    },
    {
        "urlParams": {"URL": "http://example.com/oid/[order_id]"},
        "expected": {
            "Scheme": "http://",
            "Domain": "example",
            "Suffix": "com",
            "RegisteredDomain": "example.com",
            "Path": "/oid/[order_id]",
        },
        "description": "Square brackets in Path",
    },
]
wildcardTests = [
    {
        "urlParams": {"URL": "https://asdf.wwe.ck"},
        "expected": {
            "Scheme": "https://",
            "Domain": "asdf",
            "Suffix": "wwe.ck",
            "RegisteredDomain": "asdf.wwe.ck",
        },
        "description": "Wildcard rule | *.ck",
    },
    {
        "urlParams": {"URL": "https://asdf.www.ck"},
        "expected": {
            "Scheme": "https://",
            "SubDomain": "asdf",
            "Domain": "www",
            "Suffix": "ck",
            "RegisteredDomain": "www.ck",
        },
        "description": "Wildcard exception rule | !www.ck",
    },
    {
        "urlParams": {"URL": "https://brb.i.am.going.to.be.a.fk"},
        "expected": {
            "Scheme": "https://",
            "SubDomain": "brb.i.am.going.to",
            "Domain": "be",
            "Suffix": "a.fk",
            "RegisteredDomain": "be.a.fk",
        },
        "description": "Wildcard rule | *.fk",
    },
]
lookoutTests = [  # some tests from lookout.net
    {
        "urlParams": {"URL": "http://GOO\u200b\u2060\ufeffgoo.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {
            "URL": "http://\u0646\u0627\u0645\u0647\u200c\u0627\u06cc.urltest.lookout.net"
        },
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u0000\u0dc1\u0dca\u200d\u0dbb\u0dd3.com.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u0dc1\u0dca\u200d\u0dbb\u0dd3.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\ufeffout.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {"URL": "http://www\u00A0.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u1680.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {
            "URL": "%68%74%74%70%3a%2f%2f%77%77%77%2e%65%78%61%6d%70%6c%65%2e%63%6f%6d%2f.urltest.lookout.net"
        },
        "expected": {
            "Scheme": "",
            "SubDomain": "%68%74%74%70%3a%2f%2f%77%77%77%2e%65%78%61%6d%70%6c%65%2e%63%6f%6d%2f.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {
            "URL": "http%3a%2f%2f%77%77%77%2e%65%78%61%6d%70%6c%65%2e%63%6f%6d%2f.urltest.lookout.net"
        },
        "expected": {
            "Scheme": "",
            "SubDomain": "http%3a%2f%2f%77%77%77%2e%65%78%61%6d%70%6c%65%2e%63%6f%6d%2f.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%25.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%25.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%25DOMAIN:foobar@urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "UserInfo": "%25DOMAIN:foobar",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%30%78%63%30%2e%30%32%35%30.01%2e.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%30%78%63%30%2e%30%32%35%30.01%2e.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%30%78%63%30%2e%30%32%35%30.01.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%30%78%63%30%2e%30%32%35%30.01.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%3g%78%63%30%2e%30%32%35%30%2E.01.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%3g%78%63%30%2e%30%32%35%30%2E.01.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {
            "URL": "http://%77%77%77%2e%65%78%61%6d%70%6c%65%2e%63%6f%6d.urltest.lookout.net%3a%38%30"
        },
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%77%77%77%2e%65%78%61%6d%70%6c%65%2e%63%6f%6d.urltest.lookout",
            "Domain": "net%3a%38%30",
            "Suffix": "",
            "RegisteredDomain": "",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%A1%C1.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%A1%C1.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%E4%BD%A0%E5%A5%BD\u4f60\u597d.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%E4%BD%A0%E5%A5%BD\u4f60\u597d.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%ef%b7%90zyx.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%ef%b7%90zyx.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%ef%bc%85%ef%bc%90%ef%bc%90.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%ef%bc%85%ef%bc%90%ef%bc%90.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%ef%bc%85%ef%bc%94%ef%bc%91.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%ef%bc%85%ef%bc%94%ef%bc%91.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://%zz%66%a.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "%zz%66%a.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://-foo.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "-foo.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http:////////user:@urltest.lookout.net?foo"},
        "expected": {
            "Scheme": "http:////////",
            "UserInfo": "user:",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "?foo",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://192.168.0.1 hello.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {"URL": "http://192.168.0.257.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "192.168.0.257.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://B\u00fccher.de.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "B\u00fccher.de.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://GOO \u3000goo.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {"URL": "http://Goo%20 goo%7C|.urltest.lookout.net"},
        "expected": {"Scheme": "http://"},
        "description": "",
    },
    {
        "urlParams": {"URL": "http://[google.com.].urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "",
            "Domain": "",
            "Suffix": "",
            "RegisteredDomain": "",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://[urltest.lookout.net]/"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "",
            "Domain": "",
            "Suffix": "",
            "RegisteredDomain": "",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u001f.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u001f.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u0378.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u0378.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u03b2\u03cc\u03bb\u03bf\u03c2.com.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u03b2\u03cc\u03bb\u03bf\u03c2.com.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u03b2\u03cc\u03bb\u03bf\u03c2.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u03b2\u03cc\u03bb\u03bf\u03c2.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u0442(.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u0442(.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u04c0.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u04c0.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u06dd.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u06dd.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u09dc.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u09dc.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u15ef\u15ef\u15ef.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u15ef\u15ef\u15ef.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u180e.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u180e.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u1e9e.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u1e9e.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u2183.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u2183.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u2665.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u2665.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\u4f60\u597d\u4f60\u597d.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\u4f60\u597d\u4f60\u597d.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\ufdd0zyx.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\ufdd0zyx.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\uff05\uff10\uff10.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\uff05\uff10\uff10.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\uff05\uff14\uff11.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\uff05\uff14\uff11.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {
            "URL": "http://\uff10\uff38\uff43\uff10\uff0e\uff10\uff12\uff15\uff10\uff0e\uff10\uff11.urltest.lookout.net"
        },
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\uff10\uff38\uff43\uff10\uff0e\uff10\uff12\uff15\uff10\uff0e\uff10\uff11.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://\uff27\uff4f.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "\uff27\uff4f.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://ab--cd.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "ab--cd.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://fa\u00df.de.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "fa\u00df.de.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://foo-.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "foo-.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://foo\u0300.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "foo\u0300.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://gOoGle.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "gOoGle.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://hello%00.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "hello%00.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\u0341out.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "look\u0341out.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\u034fout.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "look\u034fout.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\u05beout.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "look\u05beout.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\u202eout.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "look\u202eout.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\u2060.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "look\u2060.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\u206bout.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "look\u206bout.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\u2ff0out.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "look\u2ff0out.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://look\ufffaout.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "look\ufffaout.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://uRLTest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "uRLTest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/%20foo"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/%20foo",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/%3A%3a%3C%3c"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/%3A%3a%3C%3c",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/%7Ffp3%3Eju%3Dduvgw%3Dd"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/%7Ffp3%3Eju%3Dduvgw%3Dd",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/%A1%C1/?foo=%EF%BD%81"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/%A1%C1/?foo=%EF%BD%81",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/%A1%C1/?foo=???"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/%A1%C1/?foo=???",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/%EF%BD%81/?foo=%A1%C1"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/%EF%BD%81/?foo=%A1%C1",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/(%28:%3A%29)"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/(%28:%3A%29)",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/././foo"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/././foo",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/./.foo"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/./.foo",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net////../.."},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "////../..",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/?%02hello%7f bye"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/?%02hello%7f bye",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/?%40%41123"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/?%40%41123",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/???/?foo=%A1%C1"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/???/?foo=%A1%C1",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/?D%C3%BCrst"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/?D%C3%BCrst",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/?D%FCrst"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/?D%FCrst",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/?as?df"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/?as?df",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/?foo=bar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/?foo=bar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/?q=&lt;asdf&gt;"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/?q=&lt;asdf&gt;",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": 'http://urltest.lookout.net/?q="asdf"'},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": '/?q="asdf"',
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/?q=\u4f60\u597d"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/?q=\u4f60\u597d",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/@asdf%40"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/@asdf%40",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/D%C3%BCrst"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/D%C3%BCrst",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/D%FCrst"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/D%FCrst",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/\u2025/foo"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/\u2025/foo",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/\u202e/foo/\u202d/bar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/\u202e/foo/\u202d/bar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/\u4f60\u597d\u4f60\u597d"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/\u4f60\u597d\u4f60\u597d",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/\ufdd0zyx"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/\ufdd0zyx",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/\ufeff/foo"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/\ufeff/foo",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {
            "URL": "http://urltest.lookout.net/foo    bar/?   foo   =   bar     #    foo"
        },
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo    bar/?   foo   =   bar     #    foo",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%00%51"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%00%51",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%2"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%2",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%2Ehtml"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%2Ehtml",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%2\u00c2\u00a9zbar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%2\u00c2\u00a9zbar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%2fbar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%2fbar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%2zbar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%2zbar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%3fbar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%3fbar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo%41%7a"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo%41%7a",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/%2e"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/%2e",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/%2e%2"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/%2e%2",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/%2e./%2e%2e/.%2e/%2e.bar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/%2e./%2e%2e/.%2e/%2e.bar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/."},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/.",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/../../.."},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/../../..",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/../../../ton"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/../../../ton",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/..bar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/..bar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/./"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/./",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/bar/.."},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/bar/..",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/bar/../"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/bar/../",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/bar/../ton"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/bar/../ton",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/bar/../ton/../../a"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/bar/../ton/../../a",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/bar//.."},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/bar//..",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo/bar//../.."},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo/bar//../..",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo?bar=baz#"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo?bar=baz#",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo\\tbar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo\\tbar",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net/foo\t\ufffd%91"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Path": "/foo\t\ufffd%91",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net:80/"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "Port": "80",
            "RegisteredDomain": "lookout.net",
            "Path": "/",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net::80::443/"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net::==80::==443::/"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net\\\\foo\\\\bar"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
            "Path": "\\\\foo\\\\bar",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net\u2a7480/"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest.lookout",
            "Domain": "net\u2a7480",
            "Suffix": "",
            "RegisteredDomain": "",
            "Path": "/",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://urltest.lookout.net\uff0ffoo/"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "urltest.lookout",
            "Domain": "net\uff0ffoo",
            "Suffix": "",
            "RegisteredDomain": "",
            "Path": "/",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://www.foo\u3002bar.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "www.foo\u3002bar.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://www.loo\u0138out.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "www.loo\u0138out.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http://www.lookout.\u0441\u043e\u043c.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "www.lookout.\u0441\u043e\u043c.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    # {"urlParams": {"URL": "http://www.lookout.net\uff1a80.urltest.lookout.net"}, "expected": {"Scheme": "http://", "SubDomain": "www.lookout.net\uff1a80.urltest", "Domain": "lookout", "Suffix": "net", "RegisteredDomain": "lookout.net"}, "description": "Reject full-width colon"},
    {
        "urlParams": {"URL": "http://www.lookout\u2027net.urltest.lookout.net"},
        "expected": {
            "Scheme": "http://",
            "SubDomain": "www.lookout\u2027net.urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
    # {"urlParams": {"URL": "http://www\u2025urltest.lookout.net"}, "expected": {"Scheme": "http://", "SubDomain": "", "Domain": "lookout", "Suffix": "net", "RegisteredDomain": "lookout.net"}, "description": ""},
    # {"urlParams": {"URL": "http://xn--0.urltest.lookout.net"}, "expected": {"Scheme": "http://", "SubDomain": "", "Domain": "lookout", "Suffix": "net", "RegisteredDomain": "lookout.net"}, "description": ""},
    {
        "urlParams": {"URL": "http:\\\\\\\\urltest.lookout.net\\\\foo"},
        "expected": {
            "Scheme": "http:\\\\\\\\",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
            "Path": "\\\\foo",
        },
        "description": "",
    },
    {
        "urlParams": {"URL": "http:///\\/\\/\\/\\/urltest.lookout.net"},
        "expected": {
            "Scheme": "http:///\\/\\/\\/\\/",
            "SubDomain": "urltest",
            "Domain": "lookout",
            "Suffix": "net",
            "RegisteredDomain": "lookout.net",
        },
        "description": "",
    },
]


def testHandler(extractor, test):
    return extractor.extract(test.get("urlParams", {}).get("URL", ""),
                             subdomain=not test.get(
                                "urlParams", {}).get("IgnoreSubDomains", False),
                             format=test.get("urlParams", {}).get("ConvertURLToPunyCode", False)
                                ), (
                            test.get("expected", {}).get("Scheme", ""),
                            test.get("expected", {}).get("UserInfo", ""),
                            test.get("expected", {}).get("SubDomain", ""),
                            test.get("expected", {}).get("Domain", ""),
                            test.get("expected", {}).get("Suffix", ""),
                            test.get("expected", {}).get("Port", ""),
                            test.get("expected", {}).get("Path", ""),
                            test.get("expected", {}).get("RegisteredDomain", "")
            )


class FastTLDExtractCase(unittest.TestCase):
    # schemeTests
    def testScheme(self):
        for test in schemeTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # noScheme
    def testNoScheme(self):
        for test in noSchemeTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # userInfo
    def testUserInfo(self):
        for test in userInfoTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # ipv4
    def testIPv4(self):
        for test in ipv4Tests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # ipv6
    def testIPv6(self):
        for test in ipv6Tests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # ignoreSubDomains
    def testIgnoreSubDomains(self):
        for test in ignoreSubDomainsTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # privateSuffix
    def testPrivateSuffix(self):
        for test in privateSuffixTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # periodsAndWhiteSpaces
    def testPeriodsAndWhiteSpaces(self):
        for test in periodsAndWhiteSpacesTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # invalid
    def testInvalid(self):
        for test in invalidTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # internationalTLD
    def testInternationalTLD(self):
        for test in internationalTLDTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # domainOnlySingleTLD
    def testDomainOnlySingleTLD(self):
        for test in domainOnlySingleTLDTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # path
    def testPath(self):
        for test in pathTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # wildcard
    def testWildcard(self):
        for test in wildcardTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # lookout
    def testLookout(self):
        return
        for test in lookoutTests:
            extractor = all_suffix if test.get("includePrivateSuffix", False) else no_private_suffix
            self.assertEqual(*testHandler(extractor, test))

    # Old tests
    def test_no_private_suffix_extract(self):
        self.assertEqual(
            no_private_suffix.extract("www.myownblog.blogspot.ca"),
            ("", "", "www.myownblog", "blogspot", "ca", "", "", "blogspot.ca"),
        )
        self.assertEqual(
            no_private_suffix.extract("192.168.1.1.no-ip.co.uk"),
            ("", "", "192.168.1.1", "no-ip", "co.uk", "", "", "no-ip.co.uk"),
        )

    def test_private_suffix_extract(self):
        self.assertEqual(
            all_suffix.extract("www.myownblog.blogspot.ca"),
            ("", "", "www", "myownblog", "blogspot.ca", "", "", "myownblog.blogspot.ca"),
        )
        self.assertEqual(
            all_suffix.extract("192.168.1.1.no-ip.co.uk"),
            ("", "", "192.168.1", "1", "no-ip.co.uk", "", "", "1.no-ip.co.uk"),
        )

    def test_all_extract(self):
        todo = [
            "www.google.co.uk",
            "ditu.baidu.com.cn",
            "global.prod.fastly.net",
            "www.global.prod.fastly.net",
            "map.global.prod.fastly.net",
            "www.map.global.prod.fastly.net",
        ]
        assert_list = [
            ("", "", "www", "google", "co.uk", "", "", "google.co.uk"),
            ("", "", "ditu", "baidu", "com.cn", "", "", "baidu.com.cn"),
            ("", "", "", "", "global.prod.fastly.net", "", "", ""),
            ("", "", "", "www", "global.prod.fastly.net", "", "", "www.global.prod.fastly.net"),
            ("", "", "", "map", "global.prod.fastly.net", "", "", "map.global.prod.fastly.net"),
            ("", "", "www", "map", "global.prod.fastly.net", "", "", "map.global.prod.fastly.net"),
        ]

        for t, a in zip(todo, assert_list):
            self.assertEqual(all_suffix.extract(t), a)

    def test_wildcard(self):
        todo = [
            "ck",
            "www.ck",
            "news.www.ck",
            "big.news.www.ck",
            "abc.ck",
            "123.abc.ck",
            "foo.123.abc.ck",
        ]
        assert_list = [
            ("", "", "", "", "ck", "", "", ""),
            ("", "", "", "www", "ck", "", "", "www.ck"),
            ("", "", "news", "www", "ck", "", "", "www.ck"),
            ("", "", "big.news", "www", "ck", "", "", "www.ck"),
            ("", "", "", "", "abc.ck", "", "", ""),
            ("", "", "", "123", "abc.ck", "", "", "123.abc.ck"),
            ("", "", "foo", "123", "abc.ck", "", "", "123.abc.ck"),
        ]

        for t, a in zip(todo, assert_list):
            self.assertEqual(all_suffix.extract(t), a)

    def test_not_tld(self):
        self.assertEqual(all_suffix.extract("www.abc.noexists"), ("", "", "www.abc", "noexists", "", "", "", ""))
        self.assertEqual(
            no_private_suffix.extract("www.abc.noexists"), ("", "", "www.abc", "noexists", "", "", "", "")
        )

    def test_only_dot_tld(self):
        self.assertEqual(all_suffix.extract(".com"), ("", "", "", "", "", "", "", ""))
        self.assertEqual(no_private_suffix.extract(".com"), ("", "", "", "", "", "", "", ""))

    def test_one_rule(self):
        self.assertEqual(
            all_suffix.extract("domain.biz"), ("", "", "", "domain", "biz", "", "", "domain.biz")
        )
        self.assertEqual(
            no_private_suffix.extract("domain.biz"),
            ("", "", "", "domain", "biz", "", "", "domain.biz"),
        )

    def test_only_one_wildcard(self):
        self.assertEqual(all_suffix.extract("mm"), ("", "", "", "", "mm", "", "", ""))
        self.assertEqual(all_suffix.extract("c.mm"), ("", "", "", "", "c.mm", "", "", ""))
        self.assertEqual(all_suffix.extract("b.c.mm"), ("", "", "", "b", "c.mm", "", "", "b.c.mm"))

        self.assertEqual(no_private_suffix.extract("mm"), ("", "", "", "", "mm", "", "", ""))
        self.assertEqual(no_private_suffix.extract("c.mm"), ("", "", "", "", "c.mm", "", "", ""))
        self.assertEqual(
            no_private_suffix.extract("b.c.mm"), ("", "", "", "b", "c.mm", "", "", "b.c.mm")
        )

    def test_us_k12(self):
        # k12.ak.us is a public TLD
        self.assertEqual(all_suffix.extract("ak.us"), ("", "", "", "", "ak.us", "", "", ""))
        self.assertEqual(
            all_suffix.extract("test.k12.ak.us"),
            ("", "", "", "test", "k12.ak.us", "", "", "test.k12.ak.us"),
        )
        self.assertEqual(
            all_suffix.extract("www.test.k12.ak.us"),
            ("", "", "www", "test", "k12.ak.us", "", "", "test.k12.ak.us"),
        )

        self.assertEqual(no_private_suffix.extract("ak.us"), ("", "", "", "", "ak.us", "", "", ""))
        self.assertEqual(
            no_private_suffix.extract("test.k12.ak.us"),
            ("", "", "", "test", "k12.ak.us", "", "", "test.k12.ak.us"),
        )
        self.assertEqual(
            no_private_suffix.extract("www.test.k12.ak.us"),
            ("", "", "www", "test", "k12.ak.us", "", "", "test.k12.ak.us"),
        )

    def test_idn(self):
        self.assertEqual(
            all_suffix.extract("食狮.com.cn"), ("", "", "", "食狮", "com.cn", "", "", "食狮.com.cn")
        )

        self.assertEqual(
            no_private_suffix.extract("食狮.com.cn"),
            ("", "", "", "食狮", "com.cn", "", "", "食狮.com.cn"),
        )

    def test_punycode(self):
        self.assertEqual(
            all_suffix.extract("xn--85x722f.com.cn"),
            ("", "", "", "xn--85x722f", "com.cn", "", "", "xn--85x722f.com.cn"),
        )

        self.assertEqual(
            no_private_suffix.extract("xn--85x722f.com.cn"),
            ("", "", "", "xn--85x722f", "com.cn", "", "", "xn--85x722f.com.cn"),
        )

    def test_scheme_port_path(self):
        # no_private_suffix
        no_private_suffix_asserts = [
            ("https://", "", "", "blogspot", "com", "", "", "blogspot.com"),
            ("https://", "", "google", "blogspot", "com", "", "", "blogspot.com"),
            ("https://", "", "google", "blogspot", "com", "8080", "", "blogspot.com"),
            (
                "ftp://",
                "",
                "google",
                "blogspot",
                "com",
                "8080",
                "/a/long/path?query=42things",
                "blogspot.com",
            ),
            (
                "ftp://",
                "",
                "",
                "blogspot",
                "com",
                "8080",
                "/a/long/path?query=42things",
                "blogspot.com",
            ),
            ("https://", "", "", "blogspot", "com", "8080", "", "blogspot.com"),
        ]
        self.assertEqual(
            no_private_suffix.extract("https://blogspot.com"), no_private_suffix_asserts[0]
        )
        self.assertEqual(
            no_private_suffix.extract("https://blogspot.com", subdomain=False),
            no_private_suffix_asserts[0],
        )

        self.assertEqual(
            no_private_suffix.extract("https://google.blogspot.com"), no_private_suffix_asserts[1]
        )
        self.assertEqual(
            no_private_suffix.extract("https://google.blogspot.com", subdomain=False),
            no_private_suffix_asserts[0],
        )
        self.assertEqual(
            no_private_suffix.extract("https://google.blogspot.com:8080"),
            no_private_suffix_asserts[2],
        )
        self.assertEqual(
            no_private_suffix.extract("https://google.blogspot.com:8080", subdomain=False),
            no_private_suffix_asserts[5],
        )
        self.assertEqual(
            no_private_suffix.extract("ftp://google.blogspot.com:8080/a/long/path?query=42things"),
            no_private_suffix_asserts[3],
        )
        self.assertEqual(
            no_private_suffix.extract(
                "ftp://google.blogspot.com:8080/a/long/path?query=42things", subdomain=False
            ),
            no_private_suffix_asserts[4],
        )

        # all_suffix
        all_suffix_asserts = [
            ("https://", "", "abc", "google", "blogspot.com", "", "", "google.blogspot.com"),
            ("https://", "", "", "google", "blogspot.com", "", "", "google.blogspot.com"),
            (
                "ftp://",
                "",
                "abc",
                "google",
                "blogspot.com",
                "8080",
                "/a/long/path?query=42things",
                "google.blogspot.com",
            ),
            (
                "ftp://",
                "",
                "",
                "google",
                "blogspot.com",
                "8080",
                "/a/long/path?query=42things",
                "google.blogspot.com",
            ),
            ("https://", "", "abc", "google", "blogspot.com", "8080", "", "google.blogspot.com"),
            ("https://", "", "", "google", "blogspot.com", "8080", "", "google.blogspot.com"),
        ]
        self.assertEqual(
            all_suffix.extract("https://abc.google.blogspot.com"), all_suffix_asserts[0]
        )
        self.assertEqual(
            all_suffix.extract("https://abc.google.blogspot.com", subdomain=False),
            all_suffix_asserts[1],
        )

        self.assertEqual(
            all_suffix.extract("https://abc.google.blogspot.com"), all_suffix_asserts[0]
        )
        self.assertEqual(
            all_suffix.extract("https://abc.google.blogspot.com", subdomain=False),
            all_suffix_asserts[1],
        )
        self.assertEqual(
            all_suffix.extract("https://abc.google.blogspot.com:8080"), all_suffix_asserts[4]
        )
        self.assertEqual(
            all_suffix.extract("https://abc.google.blogspot.com:8080", subdomain=False),
            all_suffix_asserts[5],
        )
        self.assertEqual(
            all_suffix.extract("ftp://abc.google.blogspot.com:8080" "/a/long/path?query=42things"),
            all_suffix_asserts[2],
        )
        self.assertEqual(
            all_suffix.extract(
                "ftp://abc.google.blogspot.com:8080" "/a/long/path?query=42things", subdomain=False
            ),
            all_suffix_asserts[3],
        )

    def test_random_text(self):
        self.assertEqual(
            all_suffix.extract("this is a text without a domain"), ("", "", "", "", "", "", "", "")
        )
        self.assertEqual(
            all_suffix.extract("Null byte\x00string"), ("", "", "", "", "", "", "", "")
        )


if __name__ == "__main__":
    unittest.main()
