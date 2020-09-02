from impala.dbapi import connect 
from flask import request
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

conn = connect(host='localhost',port=21050) 
cur = conn.cursor() 

@app.route('/')
def home():
    return redirect('home?pages=home&tahun=2020')

@app.route('/home')
def index():
   title = "Home"
   page    = request.args.get('pages', default = 'home', type = str)
   tahun    = request.args.get('tahun', default = '2020', type = str)

   return render_template('home.html',page=page, title=title, tahun=tahun)

@app.route('/tmp')
def tmp():
    title    = "Tingkat Mutu Pelayanan"
    page    = request.args.get('pages', default = 'home', type = str)
    tahun    = request.args.get('tahun', default = 1, type = str)
    data     = request.args.get('data', default = 1, type = str)
    triwulan = request.args.get('triwulan', default = 0, type = str)
    status   = ""

    if triwulan == '1':
        start_date = '01'
        end_date = '03'
    elif triwulan == '2':
        start_date = '04'
        end_date = '06'
    elif triwulan == '3':
        start_date = '07'
        end_date = '09'
    else:
        start_date = '10'
        end_date = '12' 

    if( tahun != 1 ):
        cur.execute("SELECT count(*) from tegangan_trafo where teg_tm < 19 and YEAR(tanggal)=" + tahun)
        status_1 = cur.fetchall()

        cur.execute("SELECT count(*) from tegangan_trafo where YEAR(tanggal)="+tahun)
        status_2 = cur.fetchall()

        cur.execute("SELECT count(*) from tegangan_trafo where frek < 50 and YEAR(tanggal)="+tahun)
        status_3 = cur.fetchall()

        cur.execute("SELECT count(*) from data_ss where saidi  > 1  and  bulan >= "+ start_date +" and bulan <= " + end_date + "  and  tahun="+tahun) 
        status_4 = cur.fetchall()

        cur.execute("SELECT count(*) from data_ss where saifi > 2  and  bulan >= "+ start_date +" and bulan <= " + end_date + "  and  tahun="+tahun)
        status_5 = cur.fetchall()

        cur.execute("SELECT count(*) from hpl_gabungan " +
            " where jenis_transaksi='PASANG BARU' "+ 
            " and daya >= 200000 and durasi_hari_kerja > kriteria_tmp  "+ 
            " and substr(tglmohon,6,2) >= '"+ str(start_date) +"' and substr(tglmohon,6,2) <= '" + str(end_date) + "'  and YEAR(tglmohon)="+ tahun)
        status_6 = cur.fetchall()

        cur.execute("SELECT count(*) from hpl_gabungan " + 
            " where jenis_transaksi='PASANG BARU' " +
            " and daya < 200000 and durasi_hari_kerja > kriteria_tmp " +
            " and substr(tglmohon,6,2) >= '"+ str(start_date) +"' and substr(tglmohon,6,2) <= '" + str(end_date) + "'  and YEAR(tglmohon)="+ tahun)
        status_7 = cur.fetchall()

        cur.execute("SELECT count(*) from hpl_gabungan " +
            " where jenis_transaksi='PERUBAHAN DAYA' " +
            " and daya >= 200000 and durasi_hari_kerja > kriteria_tmp " +
            " and substr(tglmohon,6,2) >= '"+ str(start_date) +"' and substr(tglmohon,6,2) <= '" + str(end_date) + "'  and YEAR(tglmohon)="+ tahun)
        status_8 = cur.fetchall()
 
        cur.execute("SELECT count(*) from hpl_gabungan " +
            " where jenis_transaksi='PERUBAHAN DAYA' " +
                    " and daya < 200000 and durasi_hari_kerja > kriteria_tmp " +  
            " and substr(tglmohon,6,2) >= '"+ str(start_date) +"' and substr(tglmohon,6,2) <= '" + str(end_date) + "'  and YEAR(tglmohon)="+ tahun)
        status_9 = cur.fetchall()

        cur.execute("SELECT count(*) from data_response where minute(durasi_response_time) > 45 " +  
	    " and cast(substr(tgl_jam_recovery,4,2) AS int) >= "+ start_date +" and cast(substr(tgl_jam_recovery,4,2) AS int) <= " + end_date + 
	    " and cast(substr(tgl_jam_recovery,7) AS int) ="+ tahun )
        status_10 = cur.fetchall()
    	 
        cur.execute("SELECT count(*) from kor_rekening where MONTH(tanggal) >= "+ start_date +" and MONTH(tanggal) <= " + end_date + "  and YEAR  (tanggal)="+ tahun)
        status_11 = cur.fetchall()

        cur.execute("SELECT count(*) from kor_rekening where waktu_koreksi_rekening_hari > 3 and MONTH(tanggal) >= "+ start_date +" and MONTH(tanggal) <= " + end_date + "  and YEAR(tanggal)="+ tahun)
        status_12 = cur.fetchall()

        status = [ status_1[0], status_2[0], status_3[0] , status_4[0] , status_5[0] , status_6[0] , status_7[0] , status_8[0] , status_9[0] , status_10[0] , status_11[0] , status_12[0] ]
        
    
    return render_template('tmp.html', page=page, tahun = tahun, data = triwulan, title = title, status = status)

@app.route('/tmp/<years>/<data>')
def tmp_1(years,data): 
    return render_template('tmp.html', tahun=years,data=data)

## TEGANGAN TRAFO
@app.route('/tmp/indikator1/<years>/<data>')
def detail_1(years,data): 
    panel_title = 'Tegangan Menengah di Titik Pemakaian '

    cur = conn.cursor() 
    cur.execute("SELECT * from tegangan_trafo where teg_tm < 19 and YEAR(tanggal)=" + years)
    rows = cur.fetchall()

    return render_template('detail_tegangan_trafo.html',  len = len(rows), row=rows, panel_title = panel_title)

@app.route('/tmp/indikator2/<years>/<data>')
def detail_2(years,data): 
    panel_title = 'Tegangan Rendah di Titik Pemakaian'

    phasa = request.args.get('phasa', default = 0, type = str)

    if phasa == '1':
        nilai = '198' 
    else:
        nilai = '340'

    cur = conn.cursor() 
    cur.execute("SELECT * from tegangan_trafo where phasa ="+ phasa+" and TEG_UJUNG_X1_A < "+nilai+" and YEAR(tanggal)="+years)
    rows = cur.fetchall()

    return render_template('detail_tegangan_trafo.html',  len = len(rows), row=rows, panel_title = panel_title, phasa = phasa)

@app.route('/tmp/indikator3/<years>/<data>')
def detail_3(years,data):  
    panel_title = 'Frekuensi di Titik Pemakaian'

    cur = conn.cursor() 
    cur.execute("SELECT * from tegangan_trafo where frek < 50 and YEAR(tanggal)="+years)
    rows = cur.fetchall()

    return render_template('detail_tegangan_trafo.html',  len = len(rows), row=rows, panel_title = panel_title)

## SAIDI SAIFI
@app.route('/tmp/indikator4/<years>/<data>')
def detail_4(years,data): 
    panel_title = 'Lama Gangguan per Pelanggan'
    indikator = request.args.get('indikator', default = 0, type = str)

    if data == '1':
        start_date = '01'
        end_date = '04'
    elif data == '2':
        start_date = '04'
        end_date = '07'
    else:
        start_date = '07'
        end_date = '13'  

    cur = conn.cursor() 
    cur.execute("SELECT * from data_ss where saidi  > 1  and  bulan >= "+ start_date +" and bulan <= " + end_date + "  and  tahun="+years)
    rows = cur.fetchall()

    return render_template('detail_ss.html',  len = len(rows), row=rows, indikator=indikator, panel_title = panel_title)


@app.route('/tmp/indikator5/<years>/<data>')
def detail_5(years,data):  
    panel_title = 'Jumlah Gangguan per Pelanggan'
    indikator = request.args.get('indikator', default = 0, type = str)

    if data == '1':
        start_date = '01'
        end_date = '04'
    elif data == '2':
        start_date = '04'
        end_date = '07'
    else:
        start_date = '07'
        end_date = '13' 

    cur = conn.cursor() 
    cur.execute("SELECT * from data_ss where saifi > 2 and  bulan >= "+ start_date +" and bulan <= " + end_date + "  and  tahun="+years)
    rows = cur.fetchall()

    return render_template('detail_ss.html',  len = len(rows), row=rows, indikator=indikator, panel_title = panel_title)


## 6. Kecepatan Pelayanan Sambungan Baru  TM
@app.route('/tmp/indikator6/<years>/<data>')
def tmp_detail_6(years,data):  
    panel_title = 'Kecepatan Pelayanan Sambunhan Baru  TM'
    triwulan = request.args.get('triwulan', default = 0, type = str)

    if data == '1':
        start_date = '01'
        end_date = '03'
    elif data == '2':
        start_date = '04'
        end_date = '06'
    elif data == '3':
        start_date = '07'
        end_date = '09'
    else:
        start_date = '10'
        end_date = '12' 

    cur = conn.cursor() 
    cur.execute("SELECT * from hpl_gabungan " +
		" where jenis_transaksi='PASANG BARU' "+ 
		" and daya >= 200000 and durasi_hari_kerja > kriteria_tmp  "+ 
		" and substr(tglmohon,6,2) >= '"+ start_date +"' and substr(tglmohon,6,2) <= '" + end_date + "'  and YEAR(tglmohon)="+ years)

    rows = cur.fetchall()

    return render_template('detail_tmp.html',  len = len(rows), row=rows, panel_title = panel_title)

## 7. Kecepatan Pelayanan Sambungan Baru  TR
@app.route('/tmp/indikator7/<years>/<data>')
def tmp_detail_7(years=None,data=None):  
    panel_title = 'Kecepatan Pelayanan Sambunhan Baru  TR'
    triwulan = request.args.get('triwulan', default = 0, type = str)

    if data == '1':
        start_date = '01'
        end_date = '03'
    elif data == '2':
        start_date = '04'
        end_date = '06'
    elif data == '3':
        start_date = '07'
        end_date = '09'
    else:
        start_date = '10'
        end_date = '12' 

    cur = conn.cursor() 
    cur.execute("SELECT * from hpl_gabungan " + 
		" where jenis_transaksi='PASANG BARU' " +
		" and daya < 200000 and durasi_hari_kerja > kriteria_tmp " +
		" and substr(tglmohon,6,2) >= '"+ start_date +"' and substr(tglmohon,6,2) <= '" + end_date + "'  and YEAR(tglmohon)="+ years)

    rows = cur.fetchall()

    return render_template('detail_tmp.html',  len = len(rows), row=rows , panel_title = panel_title)

## 8. Kecepatan Pelayanan Perubagan Daya  TM
@app.route('/tmp/indikator8/<years>/<data>')
def tmp_detail_8(years,data):  
    panel_title = 'Kecepatan Pelayanan Perubahan Daya  TM'
    triwulan = request.args.get('triwulan', default = 0, type = str)

    if data == '1':
        start_date = '01'
        end_date = '03'
    elif data == '2':
        start_date = '04'
        end_date = '06'
    elif data == '3':
        start_date = '07'
        end_date = '09'
    else:
        start_date = '10'
        end_date = '12' 

    cur = conn.cursor() 
    cur.execute("SELECT * from hpl_gabungan " +
		" where jenis_transaksi='PERUBAHAN DAYA' " +
		" and daya >= 200000 and durasi_hari_kerja > kriteria_tmp " +
		" and substr(tglmohon,6,2) >= '"+ start_date +"' and substr(tglmohon,6,2) <= '" + end_date + "'  and YEAR(tglmohon)="+ years)

    rows = cur.fetchall()
    return render_template('detail_tmp.html',  len = len(rows), row=rows , panel_title =  panel_title)

## 9. Kecepatan Pelayanan Perubagan Daya  TR
@app.route('/tmp/indikator9/<years>/<data>')
def tmp_detail_10(years,data): 
    panel_title = ' Kecepatan Pelayanan Perubahan Daya  TR'
    triwulan = request.args.get('triwulan', default = 0, type = str)

    if data == '1':
        start_date = '01'
        end_date = '03'
    elif data == '2':
        start_date = '04'
        end_date = '06'
    elif data == '3':
        start_date = '07'
        end_date = '09'
    else:
        start_date = '10'
        end_date = '12'  

    cur = conn.cursor() 
    cur.execute("SELECT * from hpl_gabungan " +
		   " where jenis_transaksi='PERUBAHAN DAYA' " +
                   " and daya < 200000 and durasi_hari_kerja > kriteria_tmp " +  
		   " and substr(tglmohon,6,2) >= '"+ start_date +"' and substr(tglmohon,6,2) <= '" + end_date + "'  and YEAR(tglmohon)="+ years)

    rows = cur.fetchall()

    return render_template('detail_tmp.html',  len = len(rows), row=rows , panel_title = panel_title)

## data_response
@app.route('/tmp/indikator10/<years>/<data>')
def detail_10(years,data): 
    panel_title = 'Kecepatan Menanggapi Gangguan '

    if data == '1':
        start_date = '01'
        end_date = '03'
    elif data == '2':
        start_date = '04'
        end_date = '06'
    elif data == '3':
        start_date = '07'
        end_date = '09'
    else:
        start_date = '10'
        end_date = '12'

    cur = conn.cursor() 
    cur.execute("SELECT * from data_response where minute(durasi_response_time) > 45 " +  
	" and cast(substr(tgl_jam_recovery,4,2) AS int) >= "+ start_date +" and cast(substr(tgl_jam_recovery,4,2) AS int) <= " + end_date + 
	" and cast(substr(tgl_jam_recovery,7) AS int) ="+ years)
    rows = cur.fetchall()

    return render_template('response_data.html',  len = len(rows), row=rows, panel_title = panel_title)

## kor_rekening
@app.route('/tmp/indikator11/<years>/<data>')
def detail_11(years,data): 
    panel_title = 'Kesalahan Pembacaan kWh Meter'
    triwulan = request.args.get('triwulan', default = 0, type = str)

    if data == '1':
        start_date = '01'
        end_date = '04'
    elif data == '2':
        start_date = '04'
        end_date = '07'
    else:
        start_date = '07'
        end_date = '13' 


    cur = conn.cursor() 
    cur.execute("SELECT * from kor_rekening where MONTH(tanggal) >= "+ start_date +" and MONTH(tanggal) <= " + end_date + "  and YEAR(tanggal)="+ years)
    rows = cur.fetchall()

    return render_template('detail_kor_rek.html',  len = len(rows), row=rows, panel_title = panel_title)

@app.route('/tmp/indikator12/<years>/<data>')
def detail_12(years,data): 
    panel_title = 'Waktu Koreksi Kesalahan Rekening'
    triwulan = request.args.get('triwulan', default = 0, type = str)

    if data == '1':
        start_date = '01'
        end_date = '04'
    elif data == '2':
        start_date = '04'
        end_date = '07'
    else:
        start_date = '07'
        end_date = '13' 

    cur = conn.cursor() 
    cur.execute("SELECT * from kor_rekening where waktu_koreksi_rekening_hari > 3 and MONTH(tanggal) >= "+ start_date +" and MONTH(tanggal) <= " + end_date + "  and YEAR(tanggal)="+ years)
    rows = cur.fetchall()

    return render_template('detail_kor_rek.html',  len = len(rows), row=rows, panel_title = panel_title)

@app.route('/about-us')
def aboutUs():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    ##return render_template('404.html'), 404
    return 'Sorry, halaman yang ada cari tidak ditemukan!'
 
if __name__ == '__main__':
    ##app.run(debug=True)
    app.run(use_reloader = True, debug = True) 		
