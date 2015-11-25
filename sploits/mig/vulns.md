# Mig service vulns
### AES-CBC "Evil made"
The *state* of filled forms was encrypted with AES in CBC mode and stored in browser localStorage. Since there is no checksums, it is possible to change any 2nd block of known plaintext (which is JSON) but with corrupting the previous one. You need to get proper align of 16 byte text block you want to change. 

The *state* plain text is something about:
```json
{"start": 1447920517, "join": 0, "user": {"name": "1", "sname": "1", "bdate": "1", "bplace": "1", "occup": null, "empl": null, "thought": null, "phone": "1234567890ABCDEF"}, "page": 2, "offer": false, "private": false, "login": "123456700000000012"}
```

To find flags you need to change the page number. The plain text block to change is `"}, "page": 2, "`. The previous block which will be corrupted is phone number. That's why it filled with 16 bytes (max length which is permitted). To get proper align of our block you need to play with length of login. Other fields are not suitable because it correlate with padding used as prefix of plain text before encrypting (see `pad` function).

And here is the function to hack it:
```nim
proc hack(state: string, offset: int): string =
  let cipher = decode(state)
  let oldPlainBlock = "\"}, \"page\": 2, \""
  let prevCipherBlock = cipher.sub16(offset)
  let newPlainBlock = "\"}, \"page\": 4, \""
  let newCipherBlock = prevCipherBlock xor oldPlainBlock xor newPlainBlock
  encode(cipher.substr(0, offset - 1) & newCipherBlock & cipher.substr(offset + 16), 100500)
 ```

### CString and \0
Mig service uses SHA3 HMAC function to check users auth, which based on C library implementation of SHA3 (RHash). `cstring` Nim's type is used to marshal data to C implementation. `cstring` represents a pointer to a zero-terminated char array compatible to the type char* in Ansi C. But after implicit conversion `string` to `cstring` `len()` function returns incorrect length if data contains `'\0'`!

```nim
proc calc_sha3(data: cstring): array[sha3_256_hash_size, char] =
  rhash_sha3(sha3_256_hash_size * 8, data, data.len, result)
```

This means that HMAC for logins `<login>` and `<login>\0<suffix>` are equal. So the point is to login as one of citizens and steal flag from the filled form.

### MitM
Form step 3 asks you for RSA signature of some random generated value. You can request smb else's random value and get signature for it from checker. Then use signature into opponent's service! You need only to take into account that a random value expires in 4 sec.
