''' Group Findings
1. Where is the faulty algorithm?
2. How to improve it?
3. How to test for it?
4. Lessons Learned 

Explain how your team identified the fault and then arrived at the solution

What are N + 1 Queries? 
- Performance problem where app makes databases queries in a loop instead of making a single queries (infinite loop)

- The problem appears to be in the select function because you are selecing all the records instead of one individually 
'''

# 'select' function
 def select(self, from_table: str, **where: Any) -> list[dict[str, Any]]:
        """Select records from the given table based on the supplied keyword arguments."""
        with open(self.db) as f:
            data = json.load(f)

        selected: list[dict[str, Any]] = []
        for rec in data[from_table]:
            if all(rec.get(k) == v for k, v in where.items()):
                selected.append(rec)

        return selected

# possible solution -> remove 'all' key word
 def select(self, from_table: str, **where: Any) -> list[dict[str, Any]]:
        """Select records from the given table based on the supplied keyword arguments."""
        with open(self.db) as f:
            data = json.load(f)

        selected: list[dict[str, Any]] = []
        for rec in data[from_table]:
            if (rec.get(k) == v for k, v in where.items()):
                selected.append(rec)

        return selected
