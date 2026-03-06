import unittest

from app.adapters import DetectorRule, detect_in_stock


class DetectorTests(unittest.TestCase):
    def test_vmiss_rule_detects_out_of_stock(self):
        html = """
        <div class='card'>
            <h3>US.LA.TRI.Basic</h3>
            <button>Order Now</button>
            <span>0 Available</span>
        </div>
        """
        rule = DetectorRule(
            site_name="VMISS",
            url="https://example.com",
            product_name="US.LA.TRI.Basic",
            product_anchor="US.LA.TRI.Basic",
        )
        in_stock, reason = detect_in_stock(html, rule)
        self.assertFalse(in_stock)
        self.assertIn("缺货关键词", reason)

    def test_madcity_rule_detects_stock(self):
        html = """
        <div class='plan'>
            <h3>New York Amd Ryzen Standard</h3>
            <a>Order</a>
            <span>5 可用</span>
        </div>
        """
        rule = DetectorRule(
            site_name="MadcityServers",
            url="https://example.com",
            product_name="New York Amd Ryzen Standard",
            product_anchor="New York Amd Ryzen Standard",
            unavailable_tokens=("缺货中", "0 可用"),
            available_tokens=("order", "可用"),
        )
        in_stock, reason = detect_in_stock(html, rule)
        self.assertTrue(in_stock)
        self.assertIn("有货关键词", reason)


if __name__ == "__main__":
    unittest.main()
