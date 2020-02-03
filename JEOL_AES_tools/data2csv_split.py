# coding: utf-8


#このモジュールではAES(JEOL)のスペクトルファイル(スプリットスキャン)のデータ解析に用いるスクリプトを実装している
#実行内容:
# * para(パラメータ)ファイルの読み取り
# * data(バイナリデータ)ファイルの読み取り
# * 可読化ファイル(csv)ファイルの出力

import os
import os.path
import csv
import argparse
import re
import struct
import binascii
from array import array
import math
import scipy.signal

parser = argparse.ArgumentParser()
parser.add_argument("data_file_path")
parser.add_argument("param_file_path")
parser.add_argument("--encoding", default="utf_8")

options = parser.parse_args()
data_file_path = options.data_file_path
param_file_path = options.param_file_path

output_file_path_base, ext = os.path.splitext(data_file_path)


def get_key_match_values(contents, keyword, get_data_limit):
    #keywordに対応するデータをget_data_limit個取得する関数
    #contentsは改行を除いたテキストデータであるとし、"(keyword)  (keywordに対応するデータ)"と記載されているものに対して利用する。
    #取得したデータは配列として返却される。contetns内でkeywordが合致しない場合は空の配列が返却される。

    ret_data = []
    pattern = re.compile(r'^\%s\s(.+?)$' %keyword, re.MULTILINE)

    match_result = pattern.findall(contents)
    for cnt in range(0, int(get_data_limit)):
        #検索にヒットした場合は情報を取得する
        if len(match_result) > cnt:
            ret_data.append(match_result[cnt].strip())

    return ret_data

def get_key_match_multiline_str_value(contents, keyword, get_data_limit):

    #keywordに対応するデータをget_data_limit個取得する関数
    #contentsはテキストデータ、"(keyword)  (keywordに対応するデータ)(keyword終了タグ)"と記載されているものに対して利用する。
    #(keyword終了タグ)は関数内で生成され、_で区切った部分にENDを加えて再度_で展開した文字列となる。
    #(ex. 開始タグが"$AP_COMMENT"なら終了タグは"$AP_END_COMMENT"になる)
    #取得したデータは配列として返却される。contetns内でkeywordが合致しない場合は空の配列が返却される。

    ret_data = []
    keyword_split_array = keyword.split("_")
    keyword_split_array.insert(1, "END")
    keyword_end_tag = '_'.join(keyword_split_array)

    # 行をまたぐ検索を行う正規表現はルールが煩雑化するため、改行コードを取り除く
    local_contents = contents.replace('\r', '')
    local_contents = local_contents.replace('\n', '')

    # 開始タグと終了タグの位置を取得し、その間に存在する中身を取得する
    start_tag_pattern = re.compile(r'\%s' %keyword, re.MULTILINE)
    end_tag_pattern = re.compile(r'\%s' %keyword_end_tag, re.MULTILINE)
    match_start_result = start_tag_pattern.finditer(local_contents)
    match_end_result = end_tag_pattern.finditer(local_contents)
    extract_start_point = []
    extract_end_point = []

    # 開始タグの終了位置を配列に格納する
    for iter in match_start_result:
        extract_start_point.append(iter.end())

    # 終了タグの開始位置を配列に格納する
    for iter in match_end_result:
        extract_end_point.append(iter.start())

    contents_pair_cnt = min(len(extract_start_point), len(extract_end_point))
    if contents_pair_cnt != get_data_limit:
            print("[WARNING] detected diffurent input number of data from input tag name and number of data from parameter file.")
            print("input tag name: %s\ninput number of data from input tag name")
    # タグの間に存在している中身を返却用の配列に格納する
    for cnt in range(0, get_data_limit):
        # index参照エラーを防ぐため、配列要素とデータ取得要求数の比較を行う
        # 配列要素が多ければデータ取得要求数分のみを返り値の配列に格納する
        # データ取得要求数が配列要素より多ければ帰り値の配列は配列要素数の配列になる
        if contents_pair_cnt > cnt:
            ret_data.append(local_contents[extract_start_point[cnt]:extract_end_point[cnt]])
    return ret_data;

def read_param_file(param_file_path):

    #指定されたパラメータファイルを読み込み、データ取得のための情報を返却する関数
    #param_file_pathに存在するパラメータファイルを読み込み、データ読み取りに必要なデータ個数などの値を取得する

    ret_data = {}
    system_id = []
    acq_gate = []
    penergy = []
    pcurrent = []
    wide_spe_start = []
    wide_spe_stop = []
    wide_spe_step = []
    title_data = ""
    with open(param_file_path, 'r') as fid:
        file_contents = fid.read()
        data_type = get_key_match_values(file_contents, "$AP_DATATYPE", 1)
        system_id = get_key_match_values(file_contents, "$AP_SYSTEM_ID", 1)
        acq_date = get_key_match_values(file_contents, "$AP_ACQDATE", 1)
        penergy = get_key_match_values(file_contents, "$AP_PENERGY", 1)
        pcurrent = get_key_match_values(file_contents, "$AP_PCURRENT", 1)
        nof_exe = get_key_match_values(file_contents, "$AP_SPC_ROI_NOFEXE", 1)
        num_val_nof_exe = int(nof_exe[0])
        roi_spe_name = get_key_match_values(file_contents, "$AP_SPC_ROI_NAME", num_val_nof_exe)
        roi_spe_start = get_key_match_values(file_contents, "$AP_SPC_ROI_START", num_val_nof_exe)
        roi_spe_stop = get_key_match_values(file_contents, "$AP_SPC_ROI_STOP", num_val_nof_exe)
        roi_spe_step = get_key_match_values(file_contents, "$AP_SPC_ROI_STEP", num_val_nof_exe)
        roi_spe_points = get_key_match_values(file_contents, "$AP_SPC_ROI_POINTS", num_val_nof_exe)
        roi_spe_dwell = get_key_match_values(file_contents, "$AP_SPC_ROI_DWELL", num_val_nof_exe)
        title_data = get_key_match_multiline_str_value(file_contents, "$AP_COMMENT", 1)

    for roi_cnt in range(0, num_val_nof_exe):
        split_roi_name_data =  roi_spe_name[roi_cnt].split()
        split_roi_start_data =  roi_spe_start[roi_cnt].split()
        split_roi_stop_data =  roi_spe_stop[roi_cnt].split()
        split_roi_step_data =  roi_spe_step[roi_cnt].split()
        split_roi_points_data =  roi_spe_points[roi_cnt].split()
        split_roi_dwell_data =  roi_spe_dwell[roi_cnt].split()
        roi_spe_name[roi_cnt] = split_roi_name_data[1]
        roi_spe_start[roi_cnt] = float(split_roi_start_data[1])
        roi_spe_stop[roi_cnt] = float(split_roi_stop_data[1])
        roi_spe_step[roi_cnt] = float(split_roi_step_data[1])
        roi_spe_points[roi_cnt] = int(split_roi_points_data[1])
        roi_spe_dwell[roi_cnt] = float(split_roi_dwell_data[1])

    ret_data["AP_SYSTEM_ID"] = system_id
    ret_data["AP_DATATYPE"] = data_type[0]
    ret_data["AP_ACQDATE"] = acq_date[0]
    ret_data["AP_PENERGY"] = penergy
    ret_data["AP_PCURRENT"] = pcurrent
    ret_data["AP_SPC_ROI_NAME"] = roi_spe_name
    ret_data["AP_SPC_ROI_START"] = roi_spe_start
    ret_data["AP_SPC_ROI_STOP"] = roi_spe_stop
    ret_data["AP_SPC_ROI_STEP"] = roi_spe_step
    ret_data["AP_SPC_ROI_POINTS"] = roi_spe_points
    ret_data["AP_SPC_ROI_DWELL"] = roi_spe_dwell
    ret_data["#Title"] = title_data

    return ret_data

def read_data_spe_file(data_file_path, param_data_set):
    #バイナリファイルから4バイトずつ読み出し、paramで指定された個数ごとのデータを格納した配列で返す関数
    ret_data = []
    output_list = []

    with open(data_file_path, 'rb') as fid:
        fsize = os.path.getsize(data_file_path)
        for cnt in range(0, int(fsize)//4):
            data_block_array = array('B')
            # バイナリデータから1バイトの文字を4つ取得
            data_block_str = struct.unpack('cccc', fid.read(4))
            for point in range(0, len(data_block_str)):
                data_block_array.append(int(hex(ord(data_block_str[point])), 16))
            #リトルエンディアンでの4バイト数値データに変換する
            output = struct.unpack('>i', data_block_array)
            output_list.append(output[0])

    # 可読ファイル生成時に各物質のデータの区切れ位置を処理すると1関数で行う処理が非常に多くなるため
    shift_point = 0
    roi_spe_points = param_data_set['AP_SPC_ROI_POINTS']
    for roi_cnt in range(0, len(param_data_set['AP_SPC_ROI_NAME'])):
        ret_data.append(output_list[shift_point:(shift_point + roi_spe_points[roi_cnt])])
        shift_point += roi_spe_points[roi_cnt]

    return ret_data

def get_csv_write_data_param_array(key_name, param_key, param_data_set):
    # 指定されたキーワードをヘッダーとして指定されたキー名の
    # paramファイルの内容を追加したcsvファイルに記載するためのデータを返す関数
    ret_data = [key_name]
    for cnt in range(0, len(param_data_set[param_key])):
            ret_data.append(param_data_set[param_key][cnt])
    return ret_data

def write_csv_data_result_file(output_file_path, param_data_set, num_value_data_array, dimension, window_num, polynomial_num):
    #dataファイルから抽出したデータをcsvファイルへ出力する関数

    output_file_path_base = output_file_path + ".csv"
    with open(output_file_path_base, "w", newline = "") as write_fid:
        #csvファイル出力用の変数を設定
        writer = csv.writer(write_fid, delimiter = ",")
        #csvファイルに項目を記載
        mode_write_data = ['#comment']
        #dataType
        if int(param_data_set['AP_DATATYPE']) == 3 or int(param_data_set['AP_DATATYPE']) == 4:
            mode_write_data.append('AES(JEOL)spectrum')
        elif int(param_data_set['AP_DATATYPE']) == 5:
            mode_write_data.append('AES(JEOL)depth')
        else :
            mode_write_data.append('')

        writer.writerow(mode_write_data)
        writer.writerow(["#title", param_data_set["#Title"][0]])
        writer.writerow(["#dimension", 'x', 'y'])
        writer.writerow(['#x','Kinetic Energy','eV'])
        writer.writerow(['#y', 'Intensity', 'counts'])
        element_write_data = get_csv_write_data_param_array('#legend', 'AP_SPC_ROI_NAME', param_data_set)
        writer.writerow(element_write_data)

        date_data = param_data_set['AP_ACQDATE'][0:4] + '/' + \
            param_data_set['AP_ACQDATE'][4:6] + '/' + \
            param_data_set['AP_ACQDATE'][6:8] + ' ' + \
            param_data_set['AP_ACQDATE'][8:10] + ':' + \
            param_data_set['AP_ACQDATE'][10:12] + ':' + param_data_set['AP_ACQDATE'][12:14]
        writer.writerow(['#acq_date', date_data])
        #生データの値をそのままグラフ化する方針に決定したためcps変換を実行されないようにする
        writer.writerow(['#cps_conversion', 0])

        acq_time_write_data = get_csv_write_data_param_array('#acq_time', 'AP_SPC_ROI_DWELL', param_data_set)
        writer.writerow(acq_time_write_data)
        writer.writerow(['#acq_time_unit', 'ms'])
        writer.writerow(['#subplot', 0, 1, 1])

        #データ部分と項目記載の前には改行を1つ加える取り決めのため
        writer.writerow('')

        #x軸の値はstartの値からステップ幅と点数をかけたものになるため
        kinetic_energy_values = []
        tmp_kinetic_energy = []
        for roi_cnt in range(0, len(param_data_set['AP_SPC_ROI_NAME'])):
            tmp_start = param_data_set['AP_SPC_ROI_START'][roi_cnt]
            tmp_step = param_data_set['AP_SPC_ROI_STEP'][roi_cnt]

            for cnt in range(0, param_data_set['AP_SPC_ROI_POINTS'][roi_cnt]):
                tmp_kinetic_energy.append(tmp_start + tmp_step * cnt)
            kinetic_energy_values.append(tmp_kinetic_energy)
            tmp_kinetic_energy = []

        num_value_data_max_len = 0
        for cnt in range(0, len(num_value_data_array)):
            num_value_data_max_len = max(len(num_value_data_array[cnt]), num_value_data_max_len)

        for cnt in range(0, num_value_data_max_len):
            write_contents = []
            for roi_cnt in range(0, len(param_data_set['AP_SPC_ROI_NAME'])):
                if len(num_value_data_array[roi_cnt]) > cnt:
                    write_contents.append(kinetic_energy_values[roi_cnt][cnt])
                    write_contents.append(num_value_data_array[roi_cnt][cnt])
                else:
                    write_contents.append('')
                    write_contents.append('')
            # csvファイルへの出力
            writer.writerow(write_contents)


param_data_set = read_param_file(param_file_path)
#バイナリデータの読み取り
num_value_data_array = read_data_spe_file(data_file_path, param_data_set)
#csvファイルの出力
write_csv_data_result_file("./id", param_data_set, num_value_data_array, 2, 7, 2)
