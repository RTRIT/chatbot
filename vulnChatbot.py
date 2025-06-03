import sqlite3

# Predefined (vulnerable) query templates
preparedQuery = [
    "SELECT ArtistId FROM Artist WHERE Name = ?",

    "SELECT * FROM Album WHERE Title = ?",

    
    "SELECT * FROM Album WHERE ArtistId = ?",

    "SELECT AlbumId FROM Album WHERE Title = ?",
    "SELECT * FROM Track WHERE AlbumId = ?",
    
    
    "SELECT * FROM tracks WHERE ArtistId = ?",

    
    "SELECT * FROM albums WHERE ArtistId = ?",

    "SELECT * FROM Track WHERE Name = ?",

]

def setUp():
    conn = sqlite3.connect('Chinook.db')
    cursor = conn.cursor()
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # cursor.execute("SELECT * FROM Artist WHERE name = 'AC/DC'")
    # tables = cursor.fetchall()
    # print("Tables in database:")
    # for table in tables:
    #     print(table[0])
    # conn.close()

# ⚠️ This function is intentionally vulnerable to SQL Injection
def handleChatVuln(index, user_input):
    query_template = preparedQuery[index]
    print("The handleChatVuln index is : "+str(index))
    # Insecure: user input is directly inserted into the query string
    query = query_template.replace("?", f"'{user_input}'")
    # print(f"Executing vulnerable query: {query}")

    try:
        conn = sqlite3.connect('Chinook.db')
        cursor = conn.cursor()
        cursor.execute(query)
        print("This is the query "+query)
        results = cursor.fetchall()
        # Format results as string
        # if()
        if results:
            output = "\n".join(str(row) for row in results)
        else:
            output = "No results found."
        # print({"output": output})
        return {"output": output}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# Example usage
setUp()

# Try a normal input
# handleChatVuln(1, "AC/DC")

# Try an SQL injection
# handleChatVuln(3,"For Those About To Rock We Salute You")
