import sqlite3

# Nos conectamos a tu base de datos
conn = sqlite3.connect('empleados.db')
cursor = conn.cursor()

# Añadimos los 3 espacios nuevos uno por uno
try:
    cursor.execute("ALTER TABLE empleados ADD COLUMN email TEXT")
    cursor.execute("ALTER TABLE empleados ADD COLUMN tipo TEXT")
    cursor.execute("ALTER TABLE empleados ADD COLUMN foto TEXT")
    conn.commit()
    print("✅ ¡Listo! La base de datos ya tiene espacio para email, tipo y foto.")
except:
    print("⚠️ Nota: Es posible que las columnas ya existieran de un intento anterior.")

conn.close()
