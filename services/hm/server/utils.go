package main

import (
	"fmt"
	"encoding/base64"
	"crypto/md5"
	"io"
)

func decodeBase64(s string) string {
	bytes, _ := base64.StdEncoding.DecodeString(s)
	res := string(bytes)
	fmt.Println("Decoded data: ", res) //debug
	return res
}

func encodeBase64(s string) string {
	bytes := []byte(s)
	res := base64.StdEncoding.EncodeToString(bytes)
	return res
}

func split(c rune) bool {
	return c == ';' || c == ' ' //todo!
}

func md5hash(params ...string) string {
	h := md5.New()
	for _, param := range params {
		io.WriteString(h, param)
	}
	res := fmt.Sprintf("%x", h.Sum(nil))
    fmt.Println("MD5 sum: ", res) //debug
	return res
}