package main

import (
	"log"

	"github.com/gocolly/colly/v2"
)

func main() {
	// create a new collector
	c := colly.NewCollector()

	// Every part of the form data. Went to Costco, logged in with the dev tools open to the network
	// tab, and checked the logon request that was sent when I logged in
	formData := map[string]string{
		"logonId":       "",
		"logonPassword": "",
		"reLogonURL":    "",
		"isPharmacy":    "",
		"fromCheckout":  "",
		"authToken":     "",
		"redirect_uri":  "",
		"URL":           "",
	}

	// The post method encodes the form data which can be viewed here:
	// https://github.com/gocolly/colly/blob/2f09941613011bfde62cbe4a695310b42bf42d41/colly.go#L1352
	// However, filling it in with the exact data that was in my request fails (along with just doing the ID and password)
	// so I'm missing something
	err := c.Post("https://www.costco.ca/LogonForm", formData)
	if err != nil {
		log.Fatal(err)
	}

	// attach callbacks after login
	c.OnResponse(func(r *colly.Response) {
		log.Println("response received", r.StatusCode)
	})

	// start scraping
	c.Visit("https://www.costco.ca/CheckoutCartView")
}
