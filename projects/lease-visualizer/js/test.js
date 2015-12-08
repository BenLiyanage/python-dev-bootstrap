console.log ('starting tests')
describe("test month algorithm", function() {
	var current
	
	beforeEach(function() {
		leaseData = [{
								"unitName": "A101",
								"beginTimestamp": 0,
								"endTimestamp": 2,
								"rent": 1200
							}] 
		current = { 
			'rentSum': 1200, 
			'apartments': leaseData
			}
	})
	
	it("removes an apartment", function(){
		currentValue = {
			"unitName": "A101",
			"beginTimestamp": 3, 
			"endTimestamp": 4,
			"rent": 1200
		}
		previousValue = current['apartments'][0]
		checkApartmentEndDates(previousValue, currentValue, current)
		expect(current['rentSum']).toBe(0)
		expect(current['apartments'].length).toBe(0)
	})
	
	it("leaves an apartment", function() {
		currentValue = {
			"unitName": "A101",
			"beginTimestamp": 0, 
			"endTimestamp": 2,
			"rent": 1200
		}
		previousValue = current['apartments'][0]
		checkApartmentEndDates(previousValue, currentValue, current)
		expect(current['rentSum']).toBe(1200)
		expect(current['apartments'].length).toBe(1)
	})
	
	it("finds the highest earning month with one month", function(){
		result = findHighestEarningMonth(leaseData)
		expect(result['rentSum']).toBe(1200)
		expect(result['rentDate']).toBe(0)
	})
	
	it("finds the highest earning month with two months", function(){
		leaseData.push({
								"unitName": "A101",
								"beginTimestamp": 1,
								"endTimestamp": 2,
								"rent": 1200
							})
		result = findHighestEarningMonth(leaseData)
		expect(result['rentSum']).toBe(2400)
		expect(result['rentDate']).toBe(1)
	})
})