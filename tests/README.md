# wnm-test

[**weather-now-menu**](../weather-now-menu) QC tests.

```
Usage: wnm_test [language_code]...

Examples:

    wnm-test            # test all languages
    wnm-test yue        # test yue
    wnm-test lt mi      # test languages from lt to mi
```

Could be adapted and applied to your own scripts that present a subject, other than Open-Meteo API data, in Zenity dialogs.

## Dependencies

[**uni**](https://github.com/arp242/uni) for collation of unicode digits, punctuation and spacing marks in translations - useful for troubleshooting.

## Translation edge cases

Translations returned for Indo-European languages are generally consistent with the input format, i.e:

```
<index_number> [ <label_id>: <label_text> ].
```

Translations of Caucasus languages show inconsistencies though. In Armenian, Google substitues either the Armenian Comma U+055D or a full stop for the colon, and sometimes omits the space before the closing square bracket.

In Amharic, the closing square bracket may be omitted and the Ethopic full stop U+1362 may be substituted for the full stop. Parentheses may be substituted for square brackets.

Various unicode colons may be substituted for the ASCII colon and in Sanskrit it is replaced by the Devanagari Visarga combining character U+0903. In Tibetan, the Mark Shad U+0F0D at the end of the label_id is taken to be the separator.  

In a few cases, Bing may produce a better result.

Hopefully, the latest perl regex covers most edge cases.


