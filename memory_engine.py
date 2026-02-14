import chromadb
from datetime import datetime

class MemoryManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./memory_store")
        self.collection = self.client.get_or_create_collection("business_history")

    def add_event(self, supplier, event_text, date_str):
        self.collection.add(
            documents=[event_text],
            metadatas=[{"supplier": supplier, "date": date_str}],
            ids=[f"{supplier}_{date_str}_{datetime.now().timestamp()}"]
        )

    def get_weighted_memory(self, supplier):
        results = self.collection.query(
            query_texts=[f"issues with {supplier}"],
            n_results=5,
            where={"supplier": supplier}
        )
        
        weighted_results = []
        current_date = datetime.now()

        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            mem_date = datetime.strptime(meta['date'], "%Y-%m-%d")
            
            # Din calculate karo kitne purane hain
            days_old = (current_date - mem_date).days
            
            # FRESHNESS LOGIC (Lifecycle Management)
            if days_old < 180: # 6 months se kam
                status = "CRITICAL (Fresh)"
                weight = 1.0
            elif days_old < 365: # 1 saal se kam
                status = "RELEVANT (Recent)"
                weight = 0.6
            else:
                status = "STALE (Old)"
                weight = 0.2
                
            weighted_results.append({
                "issue": doc,
                "status": status,
                "weight": weight,
                "date": meta['date']
            })
            
        # Sort by weight (highest first) -> This prioritizes Critical memories
        weighted_results.sort(key=lambda x: x['weight'], reverse=True)
            
        return weighted_results