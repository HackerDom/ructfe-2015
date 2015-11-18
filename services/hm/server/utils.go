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
	return res
}

func encodeBase64(s string) string {
	bytes := []byte(s)
	res := base64.StdEncoding.EncodeToString(bytes)
	return res
}

func split(c rune) bool {
	return c == ';' || c == ' ' 
}

func md5hash(params ...string) string {
	h := md5.New()
	for _, param := range params {
		io.WriteString(h, param)
	}
	res := fmt.Sprintf("%x", h.Sum(nil))
	return res
}