# -*- coding: utf-8 -*-
import psycopg2

if __name__ == "__main__":
    conn_string = "host='localhost' dbname='segment' user='coneptum' password='tumconep2012'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    query = '''select x1,y1,x2,y2,id,filename from segment_segment where image_id=24;'''
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        filename = row[5]
        filename = filename.replace('/segments/','/1/N429OGD24KAA4HQX4TD1U2NDV82WXZHN/segments/')
        print filename
        cursor.execute("UPDATE segment_segment SET image_id = %s WHERE id = %s", [57,row[4]])
        conn.commit()



