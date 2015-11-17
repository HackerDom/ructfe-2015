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
	weight, err := strconv.Atoi(r.FormValue("Weight"))
	if err != nil {
		return nil
	}
    bp, err := strconv.Atoi(r.FormValue("BloodPressure"))
	if err != nil {
		return nil
	}
    pulse, err := strconv.Atoi(r.FormValue("Pulse"))
	if err != nil {
		return nil
	}
    wdistance, err := strconv.Atoi(r.FormValue("WalkingDistance"))
	if err != nil {
		return nil
	}
	comment := r.FormValue("Comment")
	
    result := &HealthMetrics{weight, bp, pulse, wdistance, comment}
	return result
}

func (this HealthMetrics) toString() string {
	return fmt.Sprintf("%d, %d, %d, %d, %v", this.Weight, this.BloodPressure, this.Pulse, this.WalkingDistance, this.Comment)
}