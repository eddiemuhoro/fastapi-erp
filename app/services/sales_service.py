from app.database import execute_query, execute_single_query
from typing import List, Dict, Any, Optional
from datetime import date

class SalesReportService:
    @staticmethod
    def get_today_hourly_sales() -> List[Dict[str, Any]]:
        """Get today's sales grouped by hour"""
        sql = """
            SELECT HOUR(s.tyme) AS hour, SUM(s.sale_total_cost) AS total_sales, c.symbol AS currency_name 
            FROM sales s 
            JOIN currency c ON s.currency_id=c.currency_id 
            WHERE s.date = CURDATE() 
            AND (s.type = '10' OR s.type = '14') 
            GROUP BY HOUR(s.tyme), c.currency_id 
            ORDER BY HOUR(s.tyme) ASC
        """
        return execute_query(sql)

    @staticmethod
    def get_rep_sales(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get sales by representative"""
        sql = """
            SELECT s.date, u.username, SUM(s.sale_total_cost) AS total_sales, c.symbol AS currency_name 
            FROM sales s 
            JOIN users u ON s.rep = u.id 
            JOIN currency c ON s.currency_id=c.currency_id 
            WHERE (s.type = '10' OR s.type = '14') 
            AND s.date BETWEEN %s AND %s 
            GROUP BY s.date, u.username, c.currency_id 
            ORDER BY s.date ASC, total_sales DESC
        """
        return execute_query(sql, (from_date, to_date))

    @staticmethod
    def get_location_sales(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get sales by location"""
        sql = """
            SELECT s.date, SUM(s.sale_total_cost) AS total_sales, l.locationname, c.symbol AS currency_name 
            FROM sales s 
            JOIN locations l ON s.loccode = l.loccode 
            JOIN currency c ON s.currency_id=c.currency_id 
            WHERE (s.type = '10' OR s.type = '14') 
            AND s.date BETWEEN %s AND %s 
            GROUP BY s.loccode, c.currency_id, s.date
        """
        return execute_query(sql, (from_date, to_date))

    @staticmethod
    def get_route_sales(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get sales by route with customers grouped"""
        sql = """
            SELECT 
                cr.region, 
                l.locationname, 
                c.symbol AS currency_name, 
                SUM(s.sale_total_cost) AS total_sales, 
                SUM(s.paid) AS total_amount_paid, 
                (SUM(s.sale_total_cost) - SUM(s.paid)) AS total_balance,
                cu.name AS customer_name, 
                SUM(s.sale_total_cost) AS customer_sales, 
                SUM(s.paid) AS customer_amount_paid, 
                (SUM(s.sale_total_cost) - SUM(s.paid)) AS customer_balance
            FROM sales s 
            JOIN customer_regions cr ON s.region_id = cr.region_id 
            JOIN locations l ON s.loccode = l.loccode 
            JOIN currency c ON s.currency_id = c.currency_id 
            JOIN customers cu ON s.customer_id = cu.id
            WHERE (s.type = '10' OR s.type = '14') 
            AND s.date BETWEEN %s AND %s 
            GROUP BY cr.region, l.locationname, c.symbol, cu.name 
            ORDER BY total_sales DESC
        """
        data = execute_query(sql, (from_date, to_date))
        
        # Group data by region
        grouped_data = {}
        for row in data:
            region = row['region']
            if region not in grouped_data:
                grouped_data[region] = {
                    'region': row['region'],
                    'total_sales': 0,
                    'total_amount_paid': 0,
                    'total_balance': 0,
                    'locationname': row['locationname'],
                    'currency_name': row['currency_name'],
                    'customers': []
                }
            
            grouped_data[region]['total_sales'] += float(row['customer_sales'])
            grouped_data[region]['total_amount_paid'] += float(row['customer_amount_paid'])
            grouped_data[region]['total_balance'] += float(row['customer_balance'])
            
            grouped_data[region]['customers'].append({
                'customer_name': row['customer_name'],
                'customer_sales': f"{row['customer_sales']:.2f}",
                'amount_paid': f"{row['customer_amount_paid']:.2f}",
                'balance': f"{row['customer_balance']:.2f}"
            })
        
        return list(grouped_data.values())

    @staticmethod
    def get_category_sales(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get sales by category"""
        sql = """
            SELECT c.category, si.description, SUM(si.quantity_purchased) AS qty, SUM(si.item_total_cost) AS total_sales, 
                   SUM(si.item_buy_price * si.quantity_purchased) AS cost, 
                   SUM((si.item_total_cost) - (si.item_buy_price * si.quantity_purchased)) AS margin, 
                   cur.symbol AS currency_name
            FROM sales s 
            JOIN sales_items si ON s.id=si.sale_id 
            JOIN items i ON si.item_id=i.id 
            JOIN items_categoryii c ON i.category_id=c.id 
            JOIN currency cur ON s.currency_id=cur.currency_id 
            WHERE (s.type = '10' OR s.type = '14') 
            AND s.date BETWEEN %s AND %s 
            GROUP BY c.id, cur.currency_id 
            ORDER BY total_sales DESC
        """
        return execute_query(sql, (from_date, to_date))

    @staticmethod
    def get_item_sales(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get sales by item"""
        sql = """
            SELECT si.description, SUM(si.quantity_purchased) AS qty, SUM(si.item_total_cost) AS total_sales, 
                   SUM(si.item_buy_price * si.quantity_purchased) AS cost, 
                   (SUM(si.item_total_cost) - SUM(si.item_buy_price * si.quantity_purchased)) AS margin, 
                   c.symbol AS currency_name, si.unit, l.locationname AS location
            FROM sales s 
            JOIN sales_items si ON s.id=si.sale_id 
            JOIN currency c ON s.currency_id=c.currency_id  
            JOIN locations l ON s.loccode=l.loccode
            WHERE (s.type = '10' OR s.type = '14') 
            AND s.date BETWEEN %s AND %s 
            GROUP BY si.item_id, c.currency_id, l.loccode
            ORDER BY total_sales DESC
        """
        return execute_query(sql, (from_date, to_date))

    @staticmethod
    def get_item_trend(filter_name: str) -> List[Dict[str, Any]]:
        """Get item sales trend"""
        sql = """
            SELECT si.description, s.date, SUM(si.quantity_purchased) AS qty, 
                   SUM(si.item_total_cost) AS total_sales, 
                   SUM(si.item_buy_price * si.quantity_purchased) AS cost, 
                   (SUM(si.item_total_cost) - SUM(si.item_buy_price * si.quantity_purchased)) AS margin, 
                   c.symbol AS currency_name, si.unit
            FROM sales s 
            JOIN sales_items si ON s.id=si.sale_id 
            JOIN currency c ON s.currency_id=c.currency_id  
            WHERE (s.type = '10' OR s.type = '14') 
            AND si.description = %s
            GROUP BY si.item_id, c.currency_id, s.date
            ORDER BY s.date ASC
        """
        return execute_query(sql, (filter_name,))

    @staticmethod
    def get_customer_sales(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get sales by customer"""
        sql = """
            SELECT 
                c.name, 
                SUM(s.sale_total_cost) AS total_sales, 
                SUM(s.paid) AS amount_paid, 
                SUM(s.balance) AS balance, 
                cur.symbol AS currency_name
            FROM sales s 
            JOIN customers c ON s.customer_id = c.id 
            JOIN currency cur ON s.currency_id = cur.currency_id 
            WHERE (s.type = '10' OR s.type = '14') 
            AND s.date BETWEEN %s AND %s 
            GROUP BY s.customer_id, cur.currency_id 
            ORDER BY c.name
        """
        return execute_query(sql, (from_date, to_date))

    @staticmethod
    def get_inventory_sales(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get inventory for sales"""
        sql = """
            SELECT i.id, i.itemname, l.loccode, l.locationname, st.stockid, SUM(st.qty) AS total_qty, u.unitname 
            FROM stockmoves st 
            JOIN items i ON st.stockid = i.id 
            JOIN items_units u ON st.unit_id = u.id 
            JOIN locations l ON l.loccode = st.loccode 
            GROUP BY i.id, l.loccode, st.stockid, u.unitname
        """
        return execute_query(sql)

    @staticmethod
    def get_default_sales(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get default sales data"""
        sql = """
            SELECT s.date, SUM(s.sale_total_cost) AS total_sales, c.symbol AS currency_name 
            FROM sales s 
            JOIN currency c ON s.currency_id=c.currency_id 
            WHERE (s.type = '10' OR s.type = '14') 
            AND s.date BETWEEN %s AND %s 
            GROUP BY s.date, c.currency_id
        """
        return execute_query(sql, (from_date, to_date))
