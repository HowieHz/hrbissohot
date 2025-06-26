#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈尔滨高校环境数据分析工具
用于统计和分析各学校的环境信息
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import statistics

class EnvironmentDataAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.schools_dir = self.project_root / "schools"
        
        # 学校名称映射
        self.school_names = {
            'hit': '哈尔滨工业大学',
            'heu': '哈尔滨工程大学', 
            'nefu': '东北林业大学',
            'neau': '东北农业大学',
            'hrbmu': '哈尔滨医科大学',
            'hlju': '黑龙江大学',
            'hrbnu': '哈尔滨师范大学',
            'hust': '哈尔滨理工大学'
        }
        
    def extract_temperature_data(self, content):
        """从文件内容中提取温度数据"""
        temperatures = []
        
        # 匹配温度数据的正则表达式
        temp_patterns = [
            r'室内温度[：:]\s*(\d+)°?C',
            r'室外温度[：:]\s*(\d+)°?C',
            r'最高温度[：:]\s*(\d+)°?C',
            r'最低温度[：:]\s*(\d+)°?C',
            r'(\d+)°C',  # 简单的温度格式
        ]
        
        for pattern in temp_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            temperatures.extend([int(temp) for temp in matches if temp.isdigit()])
            
        return temperatures
    
    def extract_cost_data(self, content):
        """从文件内容中提取费用数据"""
        costs = []
        
        # 匹配费用数据的正则表达式
        cost_patterns = [
            r'(\d+)元/月',
            r'费用[：:]\s*(\d+)元',
            r'(\d+)元/个',
            r'约(\d+)元',
        ]
        
        for pattern in cost_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            costs.extend([int(cost) for cost in matches if cost.isdigit()])
            
        return costs
    
    def extract_satisfaction_rating(self, content):
        """提取满意度评分"""
        rating_pattern = r'满意度[：:]\s*([⭐★]+)'
        match = re.search(rating_pattern, content)
        if match:
            return len(match.group(1))
        return None
    
    def scan_school_data(self, school_code):
        """扫描单个学校的所有数据"""
        school_path = self.schools_dir / school_code
        if not school_path.exists():
            return None
            
        school_data = {
            'school_code': school_code,
            'school_name': self.school_names.get(school_code, school_code),
            'dormitory': [],
            'cooling': [],
            'feedback': [],
            'costs': [],
            'statistics': {
                'total_reports': 0,
                'avg_temperature': None,
                'total_costs': 0,
                'avg_satisfaction': None
            }
        }
        
        # 扫描各个分类目录
        for category in ['dormitory', 'cooling', 'feedback', 'costs']:
            category_path = school_path / category
            if not category_path.exists():
                continue
                
            for file_path in category_path.glob('*.md'):
                report_data = self.parse_report_file(file_path, category)
                if report_data:
                    school_data[category].append(report_data)
                    school_data['statistics']['total_reports'] += 1
        
        # 计算统计数据
        self.calculate_school_statistics(school_data)
        return school_data
    
    def parse_report_file(self, file_path, category):
        """解析单个报告文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            title_match = re.search(r'^# (.+)', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            # 提取温度数据
            temperatures = self.extract_temperature_data(content)
            
            # 提取费用数据  
            costs = self.extract_cost_data(content)
            
            # 提取满意度
            satisfaction = self.extract_satisfaction_rating(content)
            
            # 提取可信度
            credibility_match = re.search(r'可信度[：:]\s*([⭐★]+)', content)
            credibility = len(credibility_match.group(1)) if credibility_match else None
            
            return {
                'title': title,
                'file_path': str(file_path),
                'category': category,
                'temperatures': temperatures,
                'costs': costs,
                'satisfaction': satisfaction,
                'credibility': credibility,
                'word_count': len(content),
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
            return None
    
    def calculate_school_statistics(self, school_data):
        """计算学校统计数据"""
        all_temperatures = []
        all_costs = []
        all_satisfactions = []
        
        for category in ['dormitory', 'cooling', 'feedback', 'costs']:
            for report in school_data[category]:
                all_temperatures.extend(report['temperatures'])
                all_costs.extend(report['costs'])
                if report['satisfaction']:
                    all_satisfactions.append(report['satisfaction'])
        
        # 计算平均值
        if all_temperatures:
            school_data['statistics']['avg_temperature'] = round(statistics.mean(all_temperatures), 1)
            
        if all_costs:
            school_data['statistics']['total_costs'] = sum(all_costs)
            
        if all_satisfactions:
            school_data['statistics']['avg_satisfaction'] = round(statistics.mean(all_satisfactions), 1)
    
    def generate_summary_report(self):
        """生成汇总报告"""
        all_schools_data = []
        
        # 扫描所有学校
        for school_dir in self.schools_dir.iterdir():
            if school_dir.is_dir():
                school_data = self.scan_school_data(school_dir.name)
                if school_data and school_data['statistics']['total_reports'] > 0:
                    all_schools_data.append(school_data)
        
        # 生成报告
        report = []
        report.append("# 哈尔滨高校环境数据汇总报告")
        report.append(f"\n📅 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        
        # 总体统计
        total_reports = sum(school['statistics']['total_reports'] for school in all_schools_data)
        report.append(f"\n## 📊 总体统计")
        report.append(f"- 参与学校数: {len(all_schools_data)}")
        report.append(f"- 总报告数: {total_reports}")
        
        # 各学校概况
        report.append(f"\n## 🏫 各学校情况概览")
        
        for school in sorted(all_schools_data, key=lambda x: x['statistics']['total_reports'], reverse=True):
            stats = school['statistics']
            report.append(f"\n### {school['school_name']}")
            report.append(f"- 报告数量: {stats['total_reports']}")
            
            if stats['avg_temperature']:
                report.append(f"- 平均温度: {stats['avg_temperature']}°C")
                
            if stats['avg_satisfaction']:
                satisfaction_stars = '⭐' * int(stats['avg_satisfaction'])
                report.append(f"- 平均满意度: {satisfaction_stars} ({stats['avg_satisfaction']}/5)")
                
            # 各分类报告数
            categories = ['dormitory', 'cooling', 'feedback', 'costs']
            category_names = ['宿舍环境', '降温设施', '投诉反馈', '生活成本']
            category_counts = []
            
            for cat, name in zip(categories, category_names):
                count = len(school[cat])
                if count > 0:
                    category_counts.append(f"{name}({count})")
                    
            if category_counts:
                report.append(f"- 分类情况: {' | '.join(category_counts)}")
        
        # 温度排行
        temp_schools = [(s['school_name'], s['statistics']['avg_temperature']) 
                       for s in all_schools_data 
                       if s['statistics']['avg_temperature']]
        
        if temp_schools:
            report.append(f"\n## 🌡️ 校园温度排行榜")
            temp_schools.sort(key=lambda x: x[1], reverse=True)
            for i, (name, temp) in enumerate(temp_schools, 1):
                emoji = "🔥" if i <= 3 else "😅"
                report.append(f"{i}. {name}: {temp}°C {emoji}")
        
        # 满意度排行
        satisfaction_schools = [(s['school_name'], s['statistics']['avg_satisfaction']) 
                               for s in all_schools_data 
                               if s['statistics']['avg_satisfaction']]
        
        if satisfaction_schools:
            report.append(f"\n## 😊 学生满意度排行榜")
            satisfaction_schools.sort(key=lambda x: x[1], reverse=True)
            for i, (name, rating) in enumerate(satisfaction_schools, 1):
                stars = '⭐' * int(rating)
                emoji = "👍" if rating >= 4 else "😐" if rating >= 3 else "👎"
                report.append(f"{i}. {name}: {stars} ({rating}/5) {emoji}")
        
        report.append(f"\n## 📝 数据说明")
        report.append(f"- 本报告基于学生提交的真实数据生成")
        report.append(f"- 温度数据为室内平均温度")
        report.append(f"- 满意度为学生对环境改善的评价")
        report.append(f"- 数据持续更新中，欢迎更多同学参与")
        
        return '\n'.join(report)
    
    def export_json_data(self):
        """导出JSON格式数据"""
        all_schools_data = []
        
        for school_dir in self.schools_dir.iterdir():
            if school_dir.is_dir():
                school_data = self.scan_school_data(school_dir.name)
                if school_data:
                    all_schools_data.append(school_data)
        
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_schools': len(all_schools_data),
                'total_reports': sum(s['statistics']['total_reports'] for s in all_schools_data)
            },
            'schools': all_schools_data
        }
        
        return json.dumps(export_data, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python environment_analyzer.py <项目根目录>")
        print("示例: python environment_analyzer.py .")
        return
        
    project_root = sys.argv[1]
    analyzer = EnvironmentDataAnalyzer(project_root)
    
    print("正在分析环境数据...")
    
    # 生成汇总报告
    report = analyzer.generate_summary_report()
    
    # 保存报告
    data_dir = Path(project_root) / "data"
    data_dir.mkdir(exist_ok=True)
    
    report_file = data_dir / "summary_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存JSON数据
    json_data = analyzer.export_json_data()
    json_file = data_dir / "environment_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json_data)
    
    print(f"📄 汇总报告已保存到: {report_file}")
    print(f"📊 JSON数据已保存到: {json_file}")
    print("\n" + "="*60)
    print(report)

if __name__ == "__main__":
    main()
