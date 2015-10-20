package main

import (
    "bytes"
	"io/ioutil"
    "fmt"
    "net/http"
)

func main() {
    url := "http://localhost:8000"

    var query = []byte(``)
    req, err := http.NewRequest("GET", url, bytes.NewBuffer(query))
    req.Header.Set("Cookie", "myCookie=Polina")
    req.Header.Set("Content-Type", "text/plain")

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    fmt.Println("response Status:", resp.Status)
    fmt.Println("response Headers:", resp.Header)
    body, _ := ioutil.ReadAll(resp.Body)
    fmt.Println("response Body:", string(body))
}