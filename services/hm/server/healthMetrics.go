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
	fmt.Println(name, " ", r.FormValue(name))
	res, err := strconv.Atoi(r.FormValue(name))
    if err != nil {
        logger.Println("Can't parse " + name " parameter: " + err)
    }
	return res
}

func (this HealthMetrics) toString() string {
	return fmt.Sprintf("%d, %d, %d, %d, %v", this.Weight, this.BloodPressure, this.Pulse, this.WalkingDistance, this.Comment)
}