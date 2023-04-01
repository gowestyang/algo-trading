# Data Types
* int, double, bool, char, string
* datetime: non-negative integers, UNIX time (seconds from 1970-01-01 00:00:00)
* color: non-negative integers, for example, white can be C'255,255,255' (literal), clrWhite (name), 0xFFFFFF (integrals)
* "u" for unsigned (positive): uint, ushort, ulong
* `NormalizeDouble(double, int digits)`: useful to **prevent broker error** caused by invalid double precision
    * Note that it is not perfect, and it does not change the print output.
    * Use `DoubleToString(double, int digits)` for printing floating numbers.

## Type Casting and Conversions
* `(type)data`, `type(data)`, `(type)(data)`
* To string:
    * `string ShortToString(ushort)`: converts Unicode to its char
    * `string IntegerToString(int number, int length=0, ushort filler='')`: for example
        * `IntegerToString(1, 0)` yields "1"
        * `IntegerToString(1, 5)` yields "    1"
        * `IntegerToString(1, 5, 45)` yields "----1"
    * `DoubleToString(double, int digits)` for printing floating numbers.
    * `TimeToString(datetime, int mode)`: mode can be `TIME_DATE`, `TIME_MINUTES`, `TIME_SECONDS`, for example:
        * `TimeToString(dt, TIME_DATE);`, `TimeToString(dt, TIME_DATE|TIME_SECONDS);`, `TimeToString(dt, TIME_DATE|TIME_MINUTES|TIME_SECONDS);`
    * `EnumToString(enum)`: for example
        * `Print(MODE_SMA);` yields 0
        * `Print(EnumToString(MODE_SMA));` yields MODE_SMA
        * `Print(EnumToString((ENUM_MA_METHOD)0));` also yields MODE_SMA
        * cannot convert string to enum
* To number: `StringToInteger(string)`, `StringToDouble(string)`
    * note, for example, `StringToInteger("ABC3XYZ")` yields 0
* Time
    * `datetime StringToTime(string)`: time formats
        * "yyyy.mm.dd" or "yyyymmdd" or "yyyy/mm/dd" or "yyyy-mm-dd" + "[hh:mm]" or "[hh:mm:ss]" or "[hhmmss]"
        * note that when you print a datetime, it presents its integer value

# Variables
* `input` variables cannot be modified.
* `static` variables can be declared within functions, and their values peresist between function calls.
    * but the scope of static vairables are NOT global.
* constant is declared by `#define`
    * `#define PI 3.1415`
    * `#define AREA(pi, r) pi * r * r`
* enumarations
    * `enum ENUM_TOGGLE {ON, OFF};`
    * `ENUM_TOGGLE short_toggle;`

# Functions
* All functions are global – cannot declare functions within a function
* Use “&” in function declaration to pass by reference – use sparsely
* Print `__FUNCTION__` to identify part of the source code the message is coming from

# Boolean Expressions
* “&&” for AND, “||” for OR, “!” for NOT

# Mathematical Operations
* `bool MathIsValidNumber(x)`
* `int MathRound(x)` or simply `round(x)`
* `int MathFloor()`, `int MathCeil()`
* `MathMin(a, b)`, `MathMax(a, b)`
* `MathAbs(x)`
* `MathMod(x, y)` = x % y
* `MathPow(base, exponent)`
* `MathExp(x)`, `MathExpm1(x)` = MathExp(x) – 1
* `MathSqrt(x)`
* `MathLog(x)` = ln(x), `MathLog10(x)`, `MathLog1p(x)` = ln(1+x)
* Trigonometric:
    * `MathSin(rad)`, `MathCos(rad)`, `MathTan(rad)`
    * Inverse (Arc), Hyperbolic (h), Inverse Hyperbolic (Arc, h)

**zero dividion** will cause **critical error** - the program will be force-stopped
* remeber to check your divisor between divide by it!

# Random Number
* MathRand() yield a number from range [0, 32767]
    * One way to make it yield in a selected range is by using MathMod(dividend, divisor). The resulted range will be [0, divisor-1]
        * For example, to yield [0, 1]: `int random = MathMod(MathRand(), 2);`
        * Must do `void MathSrand(seed)` to select seed
            * Example of seed can be `TimeCurrent()`, `GetTickCount()`

# String Functions
* `bool StringAdd(&str, substr)`
* `int StringConcatenate(&str, substr1, substr2, ...)`: returns the number of chars in the string
* `int StringLen(str)`
* `string StringSubstr(str, int start_pos, int length)`: use -1 as length to copy the rest of the string
* `StringReplace(&str, string find, string replace)`: replace all instances of find

# Time Functions
* Server-based
    * `TimeCurrent()`: returns the last known server time (based on latest tick)
* Local-based (computer)
    * `TimeLocal()`: returns the local time
    * `TimeGMT()`: returns the time in GMT (based on local time)
    * `GetTickCount()`: returns the number of seconds elapsed since program (trading platform, not EA/script/indicator) start

# Terminal 
Properties
* `int TerminalInfoInteger(int property_id);`
    * `ENUM_TERMINAL_INFO_INTEGER`
    * `bool is_connected = (bool) TerminalInfoInteger(TERMINAL_CONNECTED);`
    * `bool is_trade_allowed = (bool) TerminalInfoInteger(TERMINAL_TRADE_ALLOWED);`
* `string TerminalInfoString(int property_id);`
    * `ENUM_TERMINAL_INFO_STRING`
    * `string data_folder = TerminalInfoString(TERMINAL_DATA_PATH);`
    * `string common_data = TerminalInfoString(TERMINAL_COMMON_DATA_PATH);`
* `double TerminalInfoDouble(int property_id);`
    * `ENUM_TERMINAL_INFO_DOUBLE`
    * `double balance = TerminalInfoDouble(TERMINAL_COMMUNITY_BALANCE);` : account balance
    * `double retransmission = TerminalInfoDouble(TERMINAL_RETRANSMISSION);` : re-transmission rate (network speed)