# phiTool - Phigros 数据管理工具
# Copyright (C) 2026 Chnynnya
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import math

DIFFICULTY_WEIGHT = 1.5
ACC_DIFF_WEIGHT = 2.0

def load_difficulty(path):
    difficulty = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                song_id = parts[0]
                diffs = []
                for i in range(1, len(parts)):
                    try:
                        d = float(parts[i])
                    except:
                        d = 0.0
                    diffs.append(d)
                difficulty[song_id] = diffs
    return difficulty

def calculate_rks(difficulty, acc):
    if acc < 55:
        return 0.0
    return difficulty * ((acc - 55) / 45) ** 2



def get_all_records(game_record, difficulty_data):
    records = []
    
    for song_id, levels in game_record.items():
        if song_id not in difficulty_data:
            continue
        
        diffs = difficulty_data[song_id]
        
        for level in range(4):
            if level >= len(levels):
                continue
            
            record = levels[level]
            if record is None:
                continue
            
            score = record[0]
            acc = record[1]
            fc = record[2]
            
            diff = diffs[level]
            if diff <= 0:
                continue
            
            rks = calculate_rks(diff, acc)
            if rks <= 0:
                continue
            
            records.append({
                'songId': song_id,
                'level': level,
                'difficulty': diff,
                'score': score,
                'acc': acc,
                'fc': fc,
                'rks': rks,
                'is_phi': (score == 1000000)
            })
    
    records.sort(key=lambda x: -x['rks'])
    return records

def calculate_final_rks(all_records):
    all_records.sort(key=lambda x: -x['rks'])
    best27 = all_records[:27]
    
    phi_candidates = [r for r in all_records if r['is_phi']]
    phi_candidates.sort(key=lambda x: -x['difficulty'])
    phi3 = phi_candidates[:3]
    
    phi_total = sum(r['difficulty'] for r in phi3)
    best_total = sum(r['rks'] for r in best27)
    
    return (best_total + phi_total) / 30

def find_recommendations(session_token, difficulty_path, save_data, target_increase=0.01, top_n=15):
    difficulty_data = load_difficulty(difficulty_path)
    
    game_record = save_data.get('gameRecord', {})
    all_records = get_all_records(game_record, difficulty_data)
    
    current_rks = calculate_final_rks(all_records)
    current_rks_display = round(current_rks, 2)
    target_rks = current_rks_display + target_increase - 0.005
    
    temp_records = sorted(all_records, key=lambda x: -x['rks'])
    best27_list = temp_records[:27]
    best27_set = set()
    for r in best27_list:
        best27_set.add(f"{r['songId']}_{r['level']}")
    
    recommendations = []
    
    for song_id, levels in game_record.items():
        if song_id not in difficulty_data:
            continue
        
        diffs = difficulty_data[song_id]
        
        for level in range(4):
            if level >= len(levels):
                continue
            
            if level >= len(diffs):
                continue
            
            current_record = levels[level]
            if current_record is None:
                current_acc = 0
            else:
                current_acc = current_record[1]
            
            diff = diffs[level]
            if diff <= 0:
                continue
            
            current_rks_value = calculate_rks(diff, current_acc)
            is_in_best27 = f"{song_id}_{level}" in best27_set
            
            target_acc = None
            best_possible_acc = 100.0
            
            temp_records = []
            for r in all_records:
                if r['songId'] == song_id and r['level'] == level:
                    temp_records.append({'rks': calculate_rks(diff, 100), 'difficulty': diff, 'is_phi': True})
                else:
                    temp_records.append(r)
            
            best_possible_rks = calculate_final_rks(temp_records)
            rks_gain_at_100 = best_possible_rks - current_rks
            
            if rks_gain_at_100 < 0.005:
                continue
            
            low_acc = max(55.01, current_acc - 5)
            high_acc = 100.0
            found_target = False
            
            for _ in range(100):
                mid_acc = (low_acc + high_acc) / 2
                test_rks = calculate_rks(diff, mid_acc)
                
                temp_records = []
                for r in all_records:
                    if r['songId'] == song_id and r['level'] == level:
                        temp_records.append({'rks': test_rks, 'difficulty': diff, 'is_phi': (mid_acc >= 100)})
                    else:
                        temp_records.append(r)
                
                temp_final = calculate_final_rks(temp_records)
                
                if temp_final >= target_rks:
                    target_acc = mid_acc
                    high_acc = mid_acc
                    found_target = True
                else:
                    low_acc = mid_acc
            
            if not found_target or target_acc is None:
                continue
            
            if target_acc > 100:
                continue
            
            acc_diff = target_acc - current_acc
            if acc_diff < 0:
                acc_diff = 0
            
            cost_score = diff * DIFFICULTY_WEIGHT + acc_diff * ACC_DIFF_WEIGHT
            
            expected_rks = calculate_rks(diff, target_acc)
            
            temp_records = []
            for r in all_records:
                if r['songId'] == song_id and r['level'] == level:
                    temp_records.append({'rks': expected_rks, 'difficulty': diff, 'is_phi': (target_acc >= 100)})
                else:
                    temp_records.append(r)
            
            temp_final = calculate_final_rks(temp_records)
            rks_gain = round(temp_final - current_rks, 4)
            
            if rks_gain >= 0.005:
                recommendations.append({
                    'songId': song_id,
                    'level': level,
                    'difficulty': diff,
                    'current_acc': round(current_acc, 2),
                    'target_acc': round(target_acc, 2),
                    'acc_needed': round(acc_diff, 2),
                    'cost_score': round(cost_score, 2),
                    'expected_rks': round(expected_rks, 2),
                    'is_in_best27': is_in_best27,
                    'current_rks': round(current_rks_value, 2),
                    'rks_gain': rks_gain,
                    'max_possible_gain': round(rks_gain_at_100, 4)
                })
    
    recommendations.sort(key=lambda x: x['cost_score'])
    
    return {
        'current_rks': current_rks,
        'target_rks': current_rks_display + target_increase,
        'recommendations': recommendations[:top_n]
    }