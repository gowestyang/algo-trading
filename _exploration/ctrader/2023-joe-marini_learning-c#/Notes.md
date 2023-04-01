# Variables and Data Types
* `var`: let program to determine the data type
* m for decimal number, i.e., `1.23m`, `0m`

# Operators
* null-coalescing: `a ?? b`: if a is null, return b, else a
* null-assign: `x ??= a`: x = a if x is null

# Program Flow
* `if(){...} else if(){...} else{}`
    * ternary operator: `<cond> ? <result true> : <result false>`
* `swith(x){case a:...;break; case b:...;break; default:...;break;}`
* `for(int i=0; i<x; i++){}`
    * `foreach (int i in nums) {}`
* `while(cond){}`, `do{} while(cond);`

# Exceptions
* `try{...} catch{...} catch{...} finally{...}`
* `try{...} catch(exception e){... e.Messgae ...}`
* `throw new ArgumentOutOfRangeException("x", "x is out of range");`

# String Operations
* `str.Length`
* `String.Concat(string[] values)`
* `String.Join(string sep, string[] values)`
* `int String.Compare(string, string)`
* `bool string.Equals(string)`
* `int string.IndexOf(char|string)`
* `int string.LastIndexOf(char|string)`
* `string string.Replace(old, new)`

# String Formatting
* {index[,alignment]:[format]}

