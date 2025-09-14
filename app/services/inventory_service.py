from app.database import execute_query, execute_single_query
from typing import List, Dict, Any, Optional
from datetime import date

class InventoryReportService:
    @staticmethod
    def get_summary() -> Dict[str, Any]:
        """Get inventory summary"""
        sql = """
            SELECT SUM(i.total_cost * st.qty) AS total_value, SUM(st.qty) AS total_quantity 
            FROM stockmoves st 
            JOIN items i ON st.stockid = i.id
        """
        return execute_single_query(sql)

    @staticmethod
    def get_stock_levels(location_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get stock levels grouped by category"""
        sql = """
            SELECT 
                c.id AS category_id,
                c.category AS category_name,
                i.id AS item_id,
                i.description AS item_name,
                SUM(st.qty) AS stock_quantity,
                MAX(st.tyme) AS last_purchased_date,
                DATEDIFF(NOW(), MAX(st.tyme)) AS days_in_inventory,
                (SUM(st.qty) * i.total_cost) AS stock_value,
                l.locationname
            FROM stockmoves st
            JOIN items i ON st.stockid = i.id
            JOIN items_categoryii c ON i.category_id = c.id
            JOIN locations l ON st.loccode = l.loccode
        """
        
        params = ()
        if location_id:
            sql += " WHERE st.loccode = %s"
            params = (location_id,)
        
        sql += " GROUP BY c.id, i.id, l.loccode ORDER BY c.id, stock_value DESC"
        
        result = execute_query(sql, params)
        
        # Group by categories
        categories = {}
        for row in result:
            category_id = row['category_id']
            
            if category_id not in categories:
                categories[category_id] = {
                    "category_id": row["category_id"],
                    "category_name": row["category_name"],
                    "total_stock_quantity": 0,
                    "total_stock_value": 0,
                    "items": [],
                }
            
            categories[category_id]["total_stock_quantity"] += row["stock_quantity"]
            categories[category_id]["total_stock_value"] += row["stock_value"]
            
            categories[category_id]["items"].append({
                "item_id": row["item_id"],
                "item_name": row["item_name"],
                "stock_quantity": row["stock_quantity"],
                "stock_value": row["stock_value"],
                "locationname": row["locationname"],
                "last_purchased_date": row["last_purchased_date"],
                "days_in_inventory": row["days_in_inventory"],
            })
        
        return list(categories.values())

    @staticmethod
    def get_low_stock(threshold: int = 10) -> List[Dict[str, Any]]:
        """Get items with low stock"""
        sql = """
            SELECT i.id, i.description, SUM(st.qty) AS stock_quantity 
            FROM stockmoves st 
            JOIN items i ON st.stockid = i.id 
            GROUP BY i.id 
            HAVING stock_quantity < %s AND stock_quantity > 0
        """
        return execute_query(sql, (threshold,))

    @staticmethod
    def get_overstock(threshold: int = 100) -> List[Dict[str, Any]]:
        """Get items with overstock"""
        sql = """
            SELECT i.id, i.description, SUM(st.qty) AS stock_quantity 
            FROM stockmoves st 
            JOIN items i ON st.stockid = i.id 
            GROUP BY i.id 
            HAVING stock_quantity > %s
        """
        return execute_query(sql, (threshold,))

    @staticmethod
    def get_top_selling(from_date: date, to_date: date, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top selling items"""
        sql = """
            SELECT si.description, SUM(si.quantity_purchased) AS qty, 
                   SUM(si.item_total_cost) AS total_sales 
            FROM sales_items si 
            JOIN sales s ON si.sale_id = s.id 
            WHERE s.date BETWEEN %s AND %s 
            GROUP BY si.item_id 
            ORDER BY total_sales DESC 
            LIMIT %s
        """
        return execute_query(sql, (from_date, to_date, limit))

    @staticmethod
    def get_slow_moving(from_date: date, to_date: date, limit: int = 5) -> List[Dict[str, Any]]:
        """Get slow moving items"""
        sql = """
            SELECT si.description, SUM(si.quantity_purchased) AS qty, 
                   SUM(si.item_total_cost) AS total_sales 
            FROM sales_items si 
            JOIN sales s ON si.sale_id = s.id 
            WHERE s.date BETWEEN %s AND %s 
            GROUP BY si.item_id 
            ORDER BY total_sales ASC 
            LIMIT %s
        """
        return execute_query(sql, (from_date, to_date, limit))

    @staticmethod
    def get_negative_quantities() -> List[Dict[str, Any]]:
        """Get items with negative stock quantities"""
        sql = """
            SELECT i.id, i.description, SUM(st.qty) AS stock_balance, l.locationname
            FROM stockmoves st 
            JOIN items i ON st.stockid = i.id 
            JOIN locations l ON l.loccode = st.loccode 
            GROUP BY i.id, l.loccode 
            HAVING stock_balance < 0
            ORDER BY stock_balance ASC
        """
        return execute_query(sql)

    @staticmethod
    def get_turnover_rate(from_date: date, to_date: date) -> Dict[str, Any]:
        """Calculate stock turnover rate"""
        # Calculate COGS
        sql_cogs = """
            SELECT SUM(si.item_buy_price * si.quantity_purchased) AS cogs
            FROM sales_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE s.date BETWEEN %s AND %s 
            AND si.item_buy_price > 0 
            AND si.quantity_purchased > 0
        """
        cogs_result = execute_single_query(sql_cogs, (from_date, to_date))
        cogs = float(cogs_result['cogs']) if cogs_result and cogs_result['cogs'] else 0
        
        # Calculate Average Inventory
        sql_inventory = """
            SELECT AVG(total_stock) AS average_inventory
            FROM (
                SELECT SUM(st.qty * i.total_cost) AS total_stock
                FROM stockmoves st
                JOIN items i ON st.stockid = i.id
                WHERE st.trandate BETWEEN %s AND %s
                AND st.qty > 0
                AND i.total_cost > 0
            ) AS inventory
        """
        inventory_result = execute_single_query(sql_inventory, (from_date, to_date))
        average_inventory = float(inventory_result['average_inventory']) if inventory_result and inventory_result['average_inventory'] else 0
        
        # Calculate turnover rate
        stock_turnover_rate = (cogs / average_inventory) if average_inventory > 0 else 0
        
        return {
            "stock_turnover_rate": round(stock_turnover_rate, 2),
            "cogs": round(cogs, 2),
            "average_inventory": round(average_inventory, 2)
        }

    @staticmethod
    def get_incoming_stock(from_date: date, to_date: date, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get incoming stock movements"""
        sql = """
            SELECT 
                st.stkmoveno,
                i.description AS item_name,
                st.qty AS quantity_received,
                i.total_cost AS unit_cost,
                (st.qty * i.total_cost) AS stock_value,
                st.tyme AS received_date,
                l.locationname AS warehouse_location
            FROM stockmoves st
            JOIN items i ON st.stockid = i.id
            JOIN locations l ON st.loccode = l.loccode
            WHERE st.qty > 0
            AND DATE(st.tyme) BETWEEN %s AND %s
        """
        
        params = [from_date, to_date]
        if location:
            sql += " AND l.locationname = %s"
            params.append(location)
        
        sql += " ORDER BY st.tyme DESC"
        
        return execute_query(sql, params)

    @staticmethod
    def get_outgoing_stock(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get outgoing stock movements"""
        sql = """
            SELECT 
                i.id AS item_id,
                i.description AS item_name,
                SUM(ABS(st.qty)) AS total_quantity_moved,
                MAX(st.tyme) AS last_transaction_date,
                l.locationname AS warehouse_location,
                SUM(ABS(st.qty) * i.total_cost) AS total_stock_value
            FROM stockmoves st
            JOIN items i ON st.stockid = i.id
            JOIN locations l ON st.loccode = l.loccode
            WHERE st.qty < 0  
            AND DATE(st.tyme) BETWEEN %s AND %s
            GROUP BY i.id, l.locationname
            ORDER BY total_stock_value DESC
        """
        return execute_query(sql, (from_date, to_date))

    @staticmethod
    def get_dead_stock(from_date: date, to_date: date, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get dead stock (items not sold in period)"""
        sql = """
            SELECT 
                i.id AS item_id, 
                i.description AS item_name, 
                c.category AS category_name, 
                SUM(st.qty) AS stock_quantity, 
                (SUM(st.qty) * i.total_cost) AS stock_value, 
                MAX(st.tyme) AS last_purchased_date,
                DATEDIFF(NOW(), MAX(st.tyme)) AS days_in_inventory,
                l.locationname AS warehouse_location
            FROM stockmoves st
            JOIN items i ON st.stockid = i.id
            JOIN locations l ON st.loccode = l.loccode
            JOIN items_categoryii c ON i.category_id = c.id
            LEFT JOIN (
                SELECT si.item_id
                FROM sales_items si
                JOIN sales s ON si.sale_id = s.id
                WHERE s.date BETWEEN %s AND %s
                GROUP BY si.item_id
            ) sales_data ON i.id = sales_data.item_id
            WHERE sales_data.item_id IS NULL
            AND st.qty > 0
            GROUP BY i.id, l.locationname, c.category
            ORDER BY stock_value DESC
        """
        return execute_query(sql, (from_date, to_date))
