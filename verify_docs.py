                  import json
import subprocess
import os

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    return result.stdout, result.stderr

def check_summary():
    print('=== summary命令验证 ===')
    stdout, stderr = run_command('python script-py/main.py summary <your_session_token>')
    try:
        data = json.loads(stdout)
        fields = list(data.keys())
        print(f'实际输出字段: {fields}')
        
        expected = ['saveVersion', 'challengeModeRank', 'rankingScore', 'gameVersion', 'avatar', 'progress', 'updateAt', 'url']
        missing = [f for f in expected if f not in fields]
        extra = [f for f in fields if f not in expected]
        
        if missing:
            print(f'缺失字段: {missing}')
        if extra:
            print(f'多余字段: {extra}')
        if not missing and not extra:
            print('✓ summary字段匹配')
    except json.JSONDecodeError:
        print('✗ JSON解析失败')

def check_b27():
    print()
    print('=== b27命令验证 ===')
    stdout, stderr = run_command('python script-py/main.py b27 <your_session_token>')
    try:
        data = json.loads(stdout)
        top_fields = list(data.keys())
        print(f'顶级字段: {top_fields}')
        
        if 'phi' in data and data['phi']:
            phi_fields = list(data['phi'][0].keys())
            print(f'phi项字段: {phi_fields}')
        
        if 'best' in data and data['best']:
            best_fields = list(data['best'][0].keys())
            print(f'best项字段: {best_fields}')
        
        expected = ['rks', 'phi', 'best']
        if all(f in top_fields for f in expected):
            print('✓ b27顶级字段匹配')
    except json.JSONDecodeError:
        print('✗ JSON解析失败')

def check_recommend():
    print()
    print('=== recommend命令验证 ===')
    stdout, stderr = run_command('python script-py/main.py recommend <your_session_token> --top 1')
    try:
        data = json.loads(stdout)
        top_fields = list(data.keys())
        print(f'顶级字段: {top_fields}')
        
        if 'recommendations' in data and data['recommendations']:
            rec_fields = list(data['recommendations'][0].keys())
            print(f'recommendations项字段: {rec_fields}')
        
        expected = ['current_rks', 'target_rks', 'recommendations']
        if all(f in top_fields for f in expected):
            print('✓ recommend顶级字段匹配')
    except json.JSONDecodeError:
        print('✗ JSON解析失败')

def check_save():
    print()
    print('=== save命令验证 ===')
    stdout, stderr = run_command('python script-py/main.py save <your_session_token>')
    try:
        data = json.loads(stdout)
        fields = list(data.keys())
        print(f'输出字段: {fields}')
        
        expected = ['status', 'encrypted_path', 'decrypted_path', 'session_token']
        if all(f in fields for f in expected):
            print('✓ save字段匹配')
    except json.JSONDecodeError:
        print('✗ JSON解析失败')

def check_readme():
    print()
    print('=== 文档字段验证 ===')
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('saveVersion', '存档版本号'),
        ('challengeModeRank', '课题模式段位'),
        ('rankingScore', '当前RKS值'),
        ('gameVersion', '游戏版本号'),
        ('avatar', '头像'),
        ('progress', '游戏进度'),
        ('updateAt', '更新时间'),
        ('url', '存档URL'),
        ('chordSupport', '双押提示'),
        ('hitSoundVolume', '打击音效'),
        ('phi', 'Phi3列表'),
        ('best', 'Best27列表'),
        ('target_acc_for_001', '提升0.01'),
        ('current_rks', '当前RKS'),
        ('target_rks', '目标RKS'),
        ('recommendations', '推荐列表'),
        ('cost_score', '成本分数'),
        ('rks_gain', 'RKS收益'),
        ('gameRecord', '游玩记录'),
        ('settings', '游戏设置'),
        ('user', '用户信息'),
        ('gameProgress', '游戏进度'),
        ('gameKey', '谱面解锁')
    ]
    
    missing = []
    for field, desc in checks:
        if f'`{field}`' not in content:
            missing.append(field)
    
    if missing:
        print(f'文档中缺失的字段: {missing}')
    else:
        print('✓ 文档字段完整')

if __name__ == '__main__':
    os.chdir('d:\\Projects\\phi\\phiTool')
    check_summary()
    check_b27()
    check_recommend()
    check_save()
    check_readme()
    print()
    print('=== 验证完成 ===')