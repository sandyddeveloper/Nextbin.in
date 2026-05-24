from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.nilagravity import NilagravityKV

async def get_kv_val(db: AsyncSession, key: str, default=None):
    """
    Retrieve value from NilagravityKV table.
    """
    result = await db.execute(select(NilagravityKV).where(NilagravityKV.key == key))
    kv_obj = result.scalar_one_or_none()
    if kv_obj is None:
        return default
    return kv_obj.value

async def set_kv_val(db: AsyncSession, key: str, value):
    """
    Insert or update a key-value pair.
    """
    result = await db.execute(select(NilagravityKV).where(NilagravityKV.key == key))
    kv_obj = result.scalar_one_or_none()
    if kv_obj is None:
        kv_obj = NilagravityKV(key=key, value=value)
        db.add(kv_obj)
    else:
        # Note: SQLAlchemy sometimes doesn't track mutations on standard JSON columns (lists/dicts)
        # when we modify in-place. Assigning a new value or using flag_modified is needed.
        # Assigning a new copy or re-assignment is safest.
        kv_obj.value = value
    await db.commit()
    return value

async def sadd_kv_val(db: AsyncSession, key: str, *members):
    """
    Simulate Redis SADD. Treats the JSON value as a list of unique members.
    Returns the number of elements added.
    """
    result = await db.execute(select(NilagravityKV).where(NilagravityKV.key == key))
    kv_obj = result.scalar_one_or_none()
    
    if kv_obj is None:
        current_list = []
        kv_obj = NilagravityKV(key=key, value=current_list)
        db.add(kv_obj)
    else:
        current_list = list(kv_obj.value) if kv_obj.value else []

    current_set = set(current_list)
    added_count = 0
    for member in members:
        if member not in current_set:
            current_set.add(member)
            current_list.append(member)
            added_count += 1
            
    kv_obj.value = current_list
    await db.commit()
    return added_count

async def smembers_kv_val(db: AsyncSession, key: str) -> list:
    """
    Simulate Redis SMEMBERS. Returns the list.
    """
    val = await get_kv_val(db, key)
    if not isinstance(val, list):
        return []
    return val

async def lpush_kv_val(db: AsyncSession, key: str, *elements):
    """
    Simulate Redis LPUSH. Prepends elements to the list.
    """
    result = await db.execute(select(NilagravityKV).where(NilagravityKV.key == key))
    kv_obj = result.scalar_one_or_none()
    
    if kv_obj is None:
        current_list = []
        kv_obj = NilagravityKV(key=key, value=current_list)
        db.add(kv_obj)
    else:
        current_list = list(kv_obj.value) if kv_obj.value else []

    # Prepend elements in order
    new_list = list(elements) + current_list
    kv_obj.value = new_list
    await db.commit()
    return len(new_list)
