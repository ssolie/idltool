# idltool
Python 2.5 and higher tool to generate code from an Amiga-style interface description.

The interface is similar to the original proprietary idltool in functionality but not all features are implemented and new features have been added.

# Credits
- Steven Solie
- Fredrik Wikström

# Changelog

## 54.8 (21.8.2022)
- Added workaround for variadic macro trailing comma issue in non-GCC compilers.
- Fixed XML parser exception handling to work in both Python 3 and 2.5.

## 54.7 (21.5.2022)
- Removed use of GCC ## token extension used in inline4 varargs macro generation The inline4 macros now require a minimum ISO C99 compiler.

## 54.6 (13.2.2021)
- Another fix for inline4 varargs macro generation.

## 54.5 (8.2.2021)
- Created this log.
- Fixed inline4 varargs macro generation.
