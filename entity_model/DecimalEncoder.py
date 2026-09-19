from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):

  def default(self, obj):
    if isinstance(obj, Decimal):
      # Convert to int if it's a whole number, otherwise float
      return int(obj) if obj % 1 == 0 else float(obj)
    return super().default(obj)