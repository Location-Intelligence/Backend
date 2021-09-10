import sys
sys.path.insert(0, '/home/tsedeniya/Documents/finalyearproject/new/Backend')
import unittest
from gridTranslation import convert_to_grid,latitude_grid,longitude_grid
test_data = [8.834616884187174, 38.659962967829706]
class GridUnitTest(unittest.TestCase):
    
    def test_convert_to_grid(self):
        self.assertAlmostEqual(convert_to_grid(test_data[0], test_data[1]),(0, 1))
        #self.assertAlmostEqual(convert_to_grid(test_data[0], test_data[1]),(0, 1))
        print("test convert to grid passed")

    def test_latitude_grid(self):
        self.assertAlmostEqual(latitude_grid(test_data[0]),0)
        print("test latitude grid passed")
    def test_longitude_grid(self):
        self.assertAlmostEqual(longitude_grid(test_data[1], test_data[0]), 1)
        print("test longitude grid passed")

if __name__ == '__main__':
    unittest.main()

