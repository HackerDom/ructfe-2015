package main

import (
	"net/http"
	"strconv"
	"fmt"
)

type HealthMetrics struct {
	Weight int
	BloodPressure int
	Pulse int
	WalkingDistance int
	Comment string
}

func parseFromForm(r *http.Request) *HealthMetrics {
	weight := getIntField(r, "Weight")
    bp := getIntField(r, "BloodPressure")
    pulse := getIntField(r, "Pulse")
    wdistance := getIntField(r, "WalkingDistance")
	comment := r.FormValue("Comment")
	
    result := &HealthMetrics{weight, bp, pulse, wdistance, comment}
	return result
}

func getIntField(r *http.Request, name string) int {
	res, err := strconv.Atoi(r.FormValue(name))
    if err != nil {
        fmt.Println(err)
    }
	return res
}