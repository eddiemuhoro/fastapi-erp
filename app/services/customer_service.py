from app.database import execute_query, execute_single_query
from typing import List, Dict, Any, Optional
from datetime import date

class CustomerReportService:
    @staticmethod
    def get_overview() -> Dict[str, Any]:
        """Get customer overview statistics"""
        sql = """
            SELECT 
                (SELECT COUNT(*) FROM customers) AS total_customers,
                (SELECT COUNT(*) FROM customers WHERE startdate >= NOW() - INTERVAL 30 DAY) AS new_customers_last_30_days,
                (SELECT COUNT(*) FROM customers WHERE lastserved >= NOW() - INTERVAL 60 DAY) AS active_customers,
                (SELECT COUNT(*) FROM customers WHERE lastserved < NOW() - INTERVAL 60 DAY) AS inactive_customers,
                (SELECT COUNT(*) FROM customers WHERE bal > 0) AS customers_with_outstanding_balance
        """
        return execute_single_query(sql)

    @staticmethod
    def get_customer_balances(as_of_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get customer balances"""
        sql = """
            SELECT c.code AS customer_id, 
                   c.name AS customer_name, 
                   c.creditlimit, 
                   c.credit, 
                   c.bal AS current_balance,
                   c.lastserved AS last_transaction_date 
            FROM customers c
        """
        
        params = ()
        if as_of_date:
            sql += " WHERE c.lastserved <= %s"
            params = (as_of_date,)
        
        sql += " ORDER BY c.lastserved DESC"
        
        return execute_query(sql, params)

    @staticmethod
    def get_due_invoices(from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Get due invoices grouped by customer"""
        sql = """
            SELECT 
                c.id AS customer_id, 
                c.name AS customer_name, 
                s.refno AS invoice_reference,
                s.due_date, 
                s.sale_total_cost AS amount_due, 
                COALESCE(s.paid, 0) AS amount_paid, 
                COALESCE(s.balance, 0) AS balance_due
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.balance > 0 
            AND s.due_date BETWEEN %s AND %s
            ORDER BY c.name, s.due_date ASC
        """
        
        rows = execute_query(sql, (from_date, to_date))
        
        # Group by customer
        grouped_data = {}
        for row in rows:
            customer_id = row['customer_id']
            
            if customer_id not in grouped_data:
                grouped_data[customer_id] = {
                    "customer_name": row['customer_name'],
                    "total_invoices": 0,
                    "total_due": 0,
                    "total_paid": 0,
                    "total_balance_due": 0,
                    "invoices": []
                }
            
            grouped_data[customer_id]["invoices"].append({
                "invoice_reference": row["invoice_reference"],
                "due_date": row["due_date"],
                "amount_due": row["amount_due"],
                "amount_paid": row["amount_paid"],
                "balance_due": row["balance_due"]
            })
            
            grouped_data[customer_id]["total_invoices"] += 1
            grouped_data[customer_id]["total_due"] += row["amount_due"]
            grouped_data[customer_id]["total_paid"] += row["amount_paid"]
            grouped_data[customer_id]["total_balance_due"] += row["balance_due"]
        
        return list(grouped_data.values())

    @staticmethod
    def get_customer_list() -> List[Dict[str, Any]]:
        """Get all customers"""
        sql = """
            SELECT 
                c.code AS customer_id, 
                c.name AS customer_name, 
                c.email, 
                c.creditlimit, 
                c.bal AS current_balance, 
                c.startdate AS joined_date, 
                c.lastserved AS last_transaction_date
            FROM customers c
            ORDER BY c.name ASC
        """
        return execute_query(sql)

    @staticmethod
    def get_aging_summary() -> List[Dict[str, Any]]:
        """Get customer aging summary"""
        sql = """
            SELECT 
                c.id, 
                c.companyid, 
                c.name, 
                u.symbol AS currency, 
                a.scurrent AS current, 
                a.d1 AS sd0, 
                a.d2 AS sd1, 
                a.d3 AS sd2, 
                a.d4 AS sd3, 
                a.stotal AS Total
            FROM aging a
            INNER JOIN customers c ON a.customercode = c.id
            INNER JOIN cust_type t ON c.cust_type = t.type_id
            INNER JOIN currency u ON c.currency_id = u.currency_id
            ORDER BY c.name ASC
        """
        return execute_query(sql)
