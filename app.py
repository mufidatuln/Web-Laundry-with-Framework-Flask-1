from flask import Flask, flash
from flask import render_template
from flask import request, redirect, url_for, session
from mysql import connector

#open conection
db = connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    database = 'db_laundry'
)
db2 = connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    database = 'db_admin'
)

if db.is_connected():
    print('open connection successful')

app = Flask(__name__)
@app.route('/')
@app.route('/home/')
def index():
    return render_template('index.html')

#Route Daftar Member
@app.route('/daftar_member/')
def member():
    return render_template('member.html')
#Route ke Halaman Layanan
@app.route('/layanan/')
def servis():
    return render_template('layanan.html')
#Route ke Halaman Form Pesan
@app.route('/form/')
def pesan():
    return render_template('formPesan.html')
#Proses Pesan dari formPesan.html
@app.route('/proses_pesan/', methods=['POST'])
def proses_pesan():
    nama = request.form['nama']
    no_telp = request.form['no_telp']
    jenis = request.form['jenis']
    berat = request.form['berat']
    member = request.form['member']
    tanggal = request.form['tanggal']
    if jenis == 'Expres':
        if member == 'ya':
            harga = int(berat)*(10000 - (0.2 * 10000))
        else:
            harga = int(berat)* 10000
    elif jenis == 'Reguler':
        if member == 'ya':
            harga = int(berat) * (5000 - (0.2 * 10000))
        else:
            harga = int(berat) * 5000
    else:
        harga = int(berat)*5000
    cur = db.cursor()
    cur.execute('INSERT INTO tbl_pesanan (nama,no_telp,jenis,berat,member,tanggal,harga) VALUES (%s,%s,%s,%s,%s,%s,%s)', 
    (nama,no_telp,jenis,berat,member,tanggal,harga))
    db.commit()
    return redirect('/nota/')

#Proses daftar member dari member.html
@app.route('/proses_daftar/', methods=['POST'])
def daftar_member():
    nama = request.form['nama']
    no_telp = request.form['no_telp']
    alamat = request.form['alamat']
    cur = db.cursor()
    cur.execute('INSERT INTO tbl_member (nama,no_telp,alamat) VALUES (%s,%s,%s)', (nama,no_telp,alamat))
    db.commit()
    return render_template('nota_member.html')
#Route untuk menampilkan nota, mengambil data base terakhir yang dikirim
@app.route('/nota/')
def nota():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_pesanan ORDER BY id_pesanan DESC LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    print(result)
    return render_template('nota.html', hasil = result)
#Route Login Admin
@app.route('/loginAdmin/', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        masuk = db2.cursor()
        masuk.execute('SELECT * FROM admin WHERE email=%s and password=%s', (email,password))
        akun = masuk.fetchone()
        if akun is None:
            flash('Login Gagal')
        elif request.form['email'] == 'admin@gmail.com' and request.form['password'] == 'password':
            return redirect(url_for('halaman_admin'))
        else:
            session['loggedin'] = True
            session['username'] = email
            flash("Login Sukses")
            return redirect(url_for('halaman_admin'))
    return render_template('login.html')

#Route untuk menampilkan halaman admin jika berhasil Login
@app.route('/admin/')
def halaman_admin():
    cursor = db.cursor()
    cursor.execute('select * from tbl_pesanan')
    result = cursor.fetchall()
    cursor.close()
    return render_template('admin.html', hasil = result)

#Route untuk ke halaman ubah data pesanan
@app.route('/ubah/<id_pesanan>')
def ubah_data_pesanan(id_pesanan):
    cur = db.cursor()
    cur.execute('SELECT * FROM tbl_pesanan where id_pesanan=%s', (id_pesanan,))
    res = cur.fetchall()
    cur.close()
    return render_template ('ubah.html', hasil = res)
    
#Route Proses Mengubah data pesanan
@app.route('/proses_ubah/', methods=['POST'])
def proses_ubah():
    id_pesanan = request.form['id_pesanan']
    nama = request.form['nama']
    no_telp = request.form['no_telp']
    jenis = request.form['jenis']
    berat = request.form['berat']
    tanggal = request.form['tanggal']
    harga = request.form['harga']
    cur = db.cursor()
    sql = "UPDATE tbl_pesanan SET nama=%s, no_telp=%s, jenis=%s, berat=%s, tanggal=%s,  harga=%s WHERE id_pesanan=%s"
    value = (nama, no_telp, jenis, berat, tanggal, harga, id_pesanan)
    cur.execute(sql,value)
    db.commit()
    return redirect(url_for('halaman_admin'))

#Route untuk menghapus data pesanan
@app.route('/hapus/<id_pesanan>', methods=['GET'])
def hapus_data(id_pesanan):
    cur = db.cursor()
    cur.execute('DELETE from tbl_pesanan where id_pesanan=%s', (id_pesanan,))
    db.commit()
    return redirect(url_for('halaman_admin'))

#Route untuk menampilkan data member My Laundry
@app.route('/data_member/')
def data_member():
    cursor = db.cursor()
    cursor.execute('select * from tbl_member')
    result = cursor.fetchall()
    cursor.close()
    return render_template('data_member.html', data = result)

#Route untuk ke halaman ubah member
@app.route('/ubah_member/<id>')
def ubah_data(id):
    cur = db.cursor()
    cur.execute('SELECT * FROM tbl_member where id=%s', (id,))
    res = cur.fetchall()
    cur.close()
    return render_template ('ubah_member.html', hasil = res)

#Route proses ubah data member
@app.route('/proses_ubah_member/', methods=['POST'])
def proses_ubah_member():
    id = request.form['id']
    nama = request.form['nama']
    no_telp = request.form['no_telp']
    alamat = request.form['alamat']
    cur = db.cursor()
    sql = "UPDATE tbl_member SET nama=%s, no_telp=%s, alamat=%s WHERE id=%s"
    value = (nama, no_telp, alamat, id)
    cur.execute(sql,value)
    db.commit()
    return redirect(url_for('data_member'))

#Route untuk menghapus data member
@app.route('/hapus_member/<id>', methods=['GET'])
def hapus_data_member(id):
    cur = db.cursor()
    cur.execute('DELETE from tbl_member where id=%s', (id,))
    db.commit()
    return redirect(url_for('data_member'))

if __name__ == '__main__':
    app.run()
