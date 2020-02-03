# coding: utf-8


#このモジュールはAES(JEOL),EPMA(JEOL)のスペクトルファイルのcsvファイルからグラフを生成する
#実行内容:
# * 可読化ファイル(csv)ファイルの読み取り
# * グラフファイル(id.png, id_over.png)の出力
import argparse
import os.path
import csv
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

parser = argparse.ArgumentParser()
parser.add_argument("file_path")
parser.add_argument("--encoding", default="utf_8")
options = parser.parse_args()
readfile = options.file_path
name, ext = os.path.splitext(readfile)

def get_key_match_values(contents, keyword, get_data_limit):
    #keywordに対応するデータをget_data_limit個取得する関数
    #contentsは改行を除いたテキストデータであるとし、"(keyword),(keywordに対応するデータ)"と記載されているものに対して利用する。
    #取得したデータは配列として返却される。contetns内でkeywordが合致しない場合は空の配列が返却される。

    ret_data = []
    pattern = re.compile(r'^\%s,(.+?)$' %keyword, re.MULTILINE)

    match_result = pattern.findall(contents)
    for cnt in range(0, int(get_data_limit)):
        #検索にヒットした場合は情報を取得する
        if len(match_result) > cnt:
            ret_data.append(match_result[cnt].strip())

    return ret_data

def create_graph(df, species_data_array, xlabel_name, y1_label_name, y2_label_name, title, write_file_name, subplot, rev_flag):
    # データフレームであるdfからspecies_data_array分の出力をまとめたグラフを出力する関数
    x = []
    y1 = []
    y2 = []
    ylim_tmp_array = []
    figure = plt.figure(figsize=(8,8))
    axis = []
    figure_area_count = 0
    #subplotが存在していない場合は1つのグラフにすべてプロットする形をとる。
    if len(subplot) != 0:
        if int(subplot[0]) == 1:
            if not (subplot[1].isdigit()) or not(subplot[2].isdigit()):
                for cnt in range(0, len(df)):
                    tmp_axis = figure.add_subplot(1, 1, 1)
                    axis.append(tmp_axis)
            else :
                row = int(subplot[1])
                col = int(subplot[2])
                for cnt in range(0, row * col):
                    axis.append(figure.add_subplot(row, col, (cnt+1)))
        else :
            tmp_axis = figure.add_subplot(1, 1, 1)
            axis.append(tmp_axis)
    else :
        tmp_axis = figure.add_subplot(1, 1, 1)
        axis.append(tmp_axis)

    axis[0].set_title(title)
    formatter = ScalarFormatter(useMathText=True)

    for axis_cnt in range(0, len(axis)):
        axis[axis_cnt].yaxis.set_major_formatter(formatter)

    for element_cnt in range(0, len(df)):
        col_num = 0
        for col in df[element_cnt].columns:
            if col_num == 0:
                x.append(df[element_cnt][col_num])
            elif col_num == 1:
                y1.append(df[element_cnt][col_num])
                # 1つのデータ系列が3であり、複数個の元素が対応している場合はsplit用のデータのとり方をしないと要求されたグラフにならないため
                if len(df[element_cnt].columns) == 3 and len(df) >= 2:
                    axis[0].plot(x[element_cnt], y1[element_cnt], lw=1, label=species_data_array[element_cnt])
                    axis[0].legend()
                    axis[0].set_xlabel(xlabel_name)
                    axis[0].set_ylabel(y1label_name)
                    if rev_flag:
                        axis[0].set_xlim(axis[0].get_xlim()[:-1])

                else:
                    axis_target = min(element_cnt, len(axis)-1)
                    axis[axis_target].plot(x[element_cnt], y1[element_cnt], lw=1, label=species_data_array[element_cnt])
                    axis[axis_target].legend()
                    axis[axis_target].set_xlabel(xlabel_name)
                    axis[axis_target].set_ylabel(y1label_name)

            elif col_num == 2:
                y2.append(df[element_cnt][col])
                ylim_tmp_array.extend(df[element_cnt][col])
                first_roi_step=x[0][1]-x[0][0]
                ylim_start_pos = int(8 / first_roi_step) + 1

                if len(df) == 1 and len(axis) == 2:
                    #AES(JEOL)のワイドスペクトルのxxx_over.png作成時にラベルが2つあり、1つの元素に対して取得をしている場合に
                    #元素数で要素を取得すると一方のラベルが参照されない状態になるため
                    tmp_label_name = species_data_array[element_cnt]
                    if len(species_data_array) > 1:
                        tmp_label_name = species_data_array[1]
                    axis[1].plot(x[element_cnt], y2[element_cnt], lw=1, label=tmp_label_name)
                    axis[1].set_xlabel(xlabel_name)
                    axis[1].legend()
                    axis[1].set_ylabel(y2label_name)
                    axis[1].set_ylim(1.5 * min(ylim_tmp_array[ylim_start_pos:]), 1.5 * max(ylim_tmp_array[ylim_start_pos:]))
                    if rev_flag:
                        axis[1].set_xlim(axis[1].get_xlim()[:-1])
                    # 1つのデータ系列が3であり、複数個の元素が対応している場合はsplit用のデータのとり方をしないと要求されたグラフにならないため
                elif len(df[element_cnt].columns) == 3 and len(df) >= 2:
                    axis[1].plot(x[element_cnt], y2[element_cnt], lw=1, label=species_data_array[element_cnt])
                    axis[1].legend()
                    axis[1].set_xlabel(xlabel_name)
                    axis[1].set_ylabel(y2label_name)
                    axis[1].set_ylim(1.5 * min(ylim_tmp_array[ylim_start_pos:]), 1.5 * max(ylim_tmp_array[ylim_start_pos:]))
                    if rev_flag:
                        axis[1].set_xlim(axis[1].get_xlim()[:-1])
                else:
                    axis_target = min(element_cnt, len(axis)-1)
                    axis[axis_target].plot(x[element_cnt], y2[element_cnt], lw=1, label=species_data_array[element_cnt])
                    axis[axis_target].legend()
                    axis[axis_target].set_xlabel(xlabel_name)
                    axis[axis_target].set_ylabel(y2label_name)
                    if axis_target != 0:
                        axis[axis_target].set_ylim(1.5 * min(ylim_tmp_array[ylim_start_pos:]), 1.5 * max(ylim_tmp_array[ylim_start_pos:]))
                        if rev_flag:
                            axis[axis_target].set_xlim(axis[element_cnt].get_xlim()[:-1])

            else:
                print("error")
            col_num += 1
    plt.tight_layout()
    plt.rcParams['font.family'] ='sans-serif'#使用するフォント
    plt.rcParams['xtick.direction'] = 'in'#x軸の目盛線が内向き('in')か外向き('out')か双方向か('inout')
    plt.rcParams['ytick.direction'] = 'in'#y軸の目盛線が内向き('in')か外向き('out')か双方向か('inout')
    plt.rcParams['xtick.major.width'] = 1.0#x軸主目盛り線の線幅
    plt.rcParams['ytick.major.width'] = 1.0#y軸主目盛り線の線幅
    plt.rcParams['axes.linewidth'] = 1.0# 軸の線幅edge linewidth。囲みの太さ

    plt.legend()
    writefile = write_file_name + '.png'
    plt.savefig(writefile,bbox_inches='tight')


def create_over_graph(df, species_data_array, xlabel_name, y1_label_name, y2_label_name, title, write_file_name, subplot, rev_flag, two_axis_flag):
    figure = plt.figure(figsize=(8,8))
    ax1 = figure.add_subplot(1,1,1)
    formatter = ScalarFormatter(useMathText=True)
    if two_axis_flag:
        ax2 = ax1.twinx()
        ax2.set_ylabel(y2label_name)
        ax2.yaxis.set_major_formatter(formatter)


    ax1.yaxis.set_major_formatter(formatter)
    if rev_flag:
        plt.gca().invert_xaxis()

    ax1.set_xlabel(xlabel_name)
    ax1.set_ylabel(y1label_name)
    plt.ticklabel_format(style="sci",  axis="y",scilimits=(0,0))
    plt.grid(True)

    x=[]
    y1=[]
    y2=[]
    #軸が異なる場合に微分値と生値のプロットの色が重なってしまうことを防ぐため
    new_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    color_cnt = 0
    plot_array = []
    for element_cnt in range(0, len(df)):
        col_num = 0
        for col in df[element_cnt].columns:
            if col_num == 0:
                x.append(df[element_cnt][col_num])
            elif col_num == 1:
                y1.append(df[element_cnt][col_num])
                over_y1_label = species_data_array[element_cnt] +'(' + y1_value_array[0] + ')'
                plot_array.append(ax1.plot(x[element_cnt], y1[element_cnt], lw=1, color=new_colors[color_cnt] ,label=over_y1_label))
            elif col_num == 2:
                y2.append(df[element_cnt][col_num])
                # この読み込みを行っている段階でaxisの数が3以上であるためy2_value_arrayには必ず情報が入っているため
                over_y2_label = species_data_array[element_cnt] +'(' + y2_value_array[0] + ')'
                if two_axis_flag:
                    plot_array.append(ax2.plot(x[element_cnt], y2[element_cnt], lw=1, color=new_colors[color_cnt],label=over_y2_label))
                else :
                    plot_array.append(ax1.plot(x[element_cnt], y2[element_cnt], lw=1, color=new_colors[color_cnt],label=over_y2_label))
            col_num += 1
            color_cnt += 1
            if color_cnt == len(new_colors):
                color_cnt = 0
    if rev_flag:
        plt.gca().invert_xaxis()
    plt.title(title)
    for cnt in range(0, len(plot_array)):
        if cnt == 0:
            lines = plot_array[cnt]
        else :
            lines += plot_array[cnt]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels)
    plt.savefig(writefile + '.png', bbox_inches='tight')

data_blocks =[]
with open(readfile, 'r') as f:

    file_contents = f.read()
    pattern = re.compile(r'^#.+?$',re.MULTILINE)
    match_result = pattern.findall(file_contents)
    skip_row_num = len(match_result)
    dimension = get_key_match_values(file_contents, '#dimension',1)
    axis_tag = dimension[0].strip().split(',')

    x_value = get_key_match_values(file_contents, '#' + axis_tag[0], 1)
    x_value_array = x_value[0].strip().split(',')
    xlabel_name = x_value_array[0]
    if x_value_array[1] != '':
        xlabel_name += '(' + x_value_array[1] + ')'

    y1_value = get_key_match_values(file_contents, '#' + axis_tag[1], 1)
    y1_value_array = y1_value[0].strip().split(',')

    y1label_name = y1_value_array[0]
    if y1_value_array[1] != '':
        y1label_name += '(' + y1_value_array[1] + ')'

    y2label_name=''
    if len(axis_tag) == 3:
        y2_value = get_key_match_values(file_contents, '#' + axis_tag[2], 1)
        y2_value_array = y2_value[0].strip().split(',')
        y2label_name = y2_value_array[0]
        if y2_value_array[1] != '':
            y2label_name += '(' + y2_value_array[1] + ')'

    rev_flag = False
    if len(x_value_array) > 3 and x_value_array[2] == 'reverse':
        rev_flag = True
    f.seek(0)
    lines = f.readlines()

    for contents in lines[skip_row_num + 1: ]:
        data_blocks.append([tmp for tmp in contents.strip().split(',')])

species_data = get_key_match_values(file_contents, '#legend', 1)
species_data_array = species_data[0].strip().split(',')

data_block_by_element=[]
if len(species_data_array) * len(axis_tag) == len(data_blocks[0]):
    for element_cnt in range(0, len(species_data_array)):
        data_block_by_element.append([])
        for row_cnt in range(0, len(data_blocks)):
            if data_blocks[row_cnt][element_cnt * len(axis_tag)]  != '':
                data_block_by_element[element_cnt].append(list(map(float,data_blocks[row_cnt][element_cnt * len(axis_tag): (element_cnt + 1) * len(axis_tag)])))

cps_conversion = get_key_match_values(file_contents, '#cps_conversion', 1)
if int(cps_conversion[0]) == 1:
    dwell_time = get_key_match_values(file_contents, '#acq_time', 1)
    dwell_unit = get_key_match_values(file_contents, '#acq_time_unit', 1)
    dwell_unit_coeff = 1
    if dwell_unit[0] == 'um':
        dwell_unit_coeff =  1/1000000
    elif dwell_unit[0] == 'ms':
        dwell_unit_coeff = 1/1000
    elif dwell_unit[0] == 'min':
        dwell_unit_coeff = 60

    dwell_time_value = []
    dwell_time_value.extend([float(tmp) * dwell_unit_coeff for tmp in dwell_time[0].strip().split(',')])
    for element_cnt in range(0, len(species_data_array)):
        for row_cnt in range(0, len(data_block_by_element[element_cnt])):
            data_block_by_element[element_cnt][row_cnt][1] /= dwell_time_value[element_cnt]
df = []
for element_cnt in range(0, len(species_data_array)):
    df.append(pd.DataFrame(data_block_by_element[element_cnt]))

title = get_key_match_values(file_contents, '#title', 1)
plt.rcParams['font.size'] = 12 #フォントの大きさ
plt.rcParams['xtick.direction'] = 'in'#x軸の目盛線が内向き('in')か外向き('out')か双方向か('inout')
plt.rcParams['font.family'] ='sans-serif'#使用するフォント
plt.rcParams['ytick.direction'] = 'in'#y軸の目盛線が内向き('in')か外向き('out')か双方向か('inout')
plt.rcParams['xtick.major.width'] = 1.0#x軸主目盛り線の線幅
plt.rcParams['ytick.major.width'] = 1.0#y軸主目盛り線の線幅
plt.rcParams['axes.linewidth'] = 1.0# 軸の線幅edge linewidth。囲みの太さ
writefile = name + '_over'

#yの2軸目が存在していない場合は軸の表記から外すため
if len(axis_tag) == 3:
    create_over_graph(df, species_data_array, xlabel_name, y1label_name, y2label_name, title[0], writefile, ['0'], rev_flag, True)
else :
    create_over_graph(df, species_data_array, xlabel_name, y1label_name, y2label_name, title[0], writefile, ['0'], rev_flag, False)

subplot_value = get_key_match_values(file_contents, '#subplot', 1)
if len(subplot_value) == 0:
    create_graph(df, species_data_array, xlabel_name, y1label_name, y2label_name, title[0], name, ['0'], rev_flag)
else:
    subplot = subplot_value[0].split(',')
    create_graph(df, species_data_array, xlabel_name, y1label_name, y2label_name, title[0], name, subplot, rev_flag)

#ワイドスペクトルの場合同じ内容の画像ファイルをもう一度出力することになるため、条件を付けてスプリットスペクトル以外は各元素の出力を行わないようにする
if len(species_data_array) != 1:
    for element_cnt in range(0, len(df)):
        #species_data_arrayはcreate_graph内でdfの要素数をもとに取得するためリストとして渡している
        write_file_name_no_ext = name + '_' + species_data_array[element_cnt] + '_' + str(element_cnt+1)
        split_title = title[0] + '(' + species_data_array[element_cnt]  + ')'
        #各元素の出力時にはsubplotの影響を受けずに一枚のグラフを出力する
        if len(axis_tag) == 3:
            create_graph([df[element_cnt]], [species_data_array[element_cnt]], xlabel_name, y1label_name, y2label_name, split_title, write_file_name_no_ext, ['1', '2', '1'], rev_flag)
        else :
            create_graph([df[element_cnt]], [species_data_array[element_cnt]], xlabel_name, y1label_name, y2label_name, split_title, write_file_name_no_ext, ['1', '1', '1'], rev_flag)
