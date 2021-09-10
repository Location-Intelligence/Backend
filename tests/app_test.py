import unittest

class UnitTestCase(unittest.TestCase):
    test_data_for_one_location = {
        "locations":
                 [
                     {
                        "id":1, 
                        "name":"4kilo",
                        "latitude":8.992021586554754,
                        "longitude":38.72606647576475
                        }
                 ]
                }
    test_data_for_multiple_location = {
        "locations":
                [
                {
                "id":1, 
                "name":"4kilo",
                "latitude":8.992021586554754,
                "longitude":38.72606647576475
                },
                {
                "id":2, 
                "name":"Mexico",
                "latitude":9.0404,
                "longitude":38.7633
                }
                ]
            }

    exceptedresult = [
    {
        "Females": 167299.0,
        "Males": 148984.0,
        "_id": "61393487834a3406cd20799c",
        "atm": 1.0,
        "bank": 18.0,
        "bus_station": 0.0,
        "church": 5.0,
        "gas_station": 3.0,
        "hospital": 4.0,
        "latitude": 8.992021586554754,
        "latitude_grid": 35.0,
        "longitude": 38.72606647576475,
        "longitude_grid": 16.0,
        "mosque": 1.0,
        "name": "4kilo",
        "nearest": [
            {
                "latitude": 8.9921785,
                "longitude": 38.7264452,
                "name": "Nardos"
            },
            {
                "latitude": 8.9926161,
                "longitude": 38.72671469999999,
                "name": "Ocean MiniMarket"
            },
            {
                "latitude": 8.9907911,
                "longitude": 38.7262752,
                "name": "Shewa Super Market"
            },
            {
                "latitude": 8.993384299999999,
                "longitude": 38.72671340000001,
                "name": "Dilgebaya"
            },
            {
                "latitude": 8.9904999,
                "longitude": 38.7263892,
                "name": "Shoa Supermarket Bisrate Gebriel"
            }
        ],
        "pharmacy": 5.0,
        "rating": 4.0,
        "restaurant": 60.0,
        "school": 30.0,
        "train_station": 0.0
    }
]
    expected_result_for_multiple_locations =[
    {
        "Females": 167299.0,
        "Males": 148984.0,
        "_id": "61393487834a3406cd20799c",
        "atm": 1.0,
        "bank": 18.0,
        "bus_station": 0.0,
        "church": 5.0,
        "gas_station": 3.0,
        "hospital": 4.0,
        "latitude": 8.992021586554754,
        "latitude_grid": 35.0,
        "longitude": 38.72606647576475,
        "longitude_grid": 16.0,
        "mosque": 1.0,
        "name": "4kilo",
        "nearest": [
            {
                "latitude": 8.9921785,
                "longitude": 38.7264452,
                "name": "Nardos"
            },
            {
                "latitude": 8.9926161,
                "longitude": 38.72671469999999,
                "name": "Ocean MiniMarket"
            },
            {
                "latitude": 8.9907911,
                "longitude": 38.7262752,
                "name": "Shewa Super Market"
            },
            {
                "latitude": 8.993384299999999,
                "longitude": 38.72671340000001,
                "name": "Dilgebaya"
            },
            {
                "latitude": 8.9904999,
                "longitude": 38.7263892,
                "name": "Shoa Supermarket Bisrate Gebriel"
            }
        ],
        "pharmacy": 5.0,
        "rating": 4.0,
        "restaurant": 60.0,
        "school": 30.0,
        "train_station": 0.0
    },
    {
        "Females": 112336,
        "Males": 99165,
        "atm": 11,
        "bank": 43,
        "bus_station": 1,
        "church": 31,
        "competitors": 60,
        "gas_station": 3,
        "hospital": 21,
        "id": 2,
        "latitude": 9.0404,
        "latitude_grid": 45,
        "longitude": 38.7633,
        "longitude_grid": 24,
        "mosque": 6,
        "name": "Mexico",
        "nearest": [
            {
                "latitude": 9.0383911,
                "longitude": 38.7650495,
                "name": "Muktar MiniMarket"
            },
            {
                "latitude": 9.0390731,
                "longitude": 38.7578403,
                "name": "Saron Mini Mrkt"
            },
            {
                "latitude": 9.0342523,
                "longitude": 38.76312900000001,
                "name": "Belonias Supermrkt"
            },
            {
                "latitude": 9.033994999999999,
                "longitude": 38.7630326,
                "name": "Belonias"
            },
            {
                "latitude": 9.0339721,
                "longitude": 38.7630325,
                "name": "Abadir supermarket"
            }
        ],
        "pharmacy": 21,
        "rating": 4,
        "restaurant": 60,
        "school": 60,
        "supermarket": 0,
        "train_station": 0
    }
]


    def test_url(self):
        resp = requests.get(self.URL)
        self.assertEqual(resp.status_code,400)
        print("test one passed")
    def test_one_location(self):
        resp = requests.post(self.URL + '/rate/',json = self.test_data_for_one_location)
        self.assertEqual(resp.status_code,200)
        self.assertEqual(resp.json(),self.exceptedresult)
        print("test by one location passed")
    def test_multiple_location(self):
        resp = requests.post(self.URL + '/rate/',json = self.test_data_for_multiple_location)
        self.assertEqual(resp.status_code,200)
        self.assertEqual(resp.json(),self.expected_result_for_multiple_locations)
        print("test by multiple location passed")

if __name__ == '__main__':
    unittest.main()
