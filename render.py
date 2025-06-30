import json
from datetime import datetime
import re

def render_html():
    # 从 data.json 加载数据
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 更新最后更新时间
    data['footer']['lastUpdate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1. 生成空调覆盖情况汇总 HTML
    ac_coverage = {
        "full": [], "basic": [], "classroom": [], "dormitory": [],
        "canteen": [], "library": [], "none": [], "pending": []
    }
    all_schools = []
    for category in data['categories']:
        all_schools.extend(category['schools'])

    for school in all_schools:
        if school.get('status') == 'pending':
            ac_coverage['pending'].append(school['name'])
            continue
        
        coverage_types = school.get('airConditioningCoverage', [])
        if not coverage_types:
            ac_coverage['none'].append(school['name'])
            continue

        coverage_count = 0
        if 'classroom' in coverage_types:
            ac_coverage['classroom'].append(school['name'])
            coverage_count += 1
        if 'dormitory' in coverage_types:
            ac_coverage['dormitory'].append(school['name'])
            coverage_count += 1
        if 'canteen' in coverage_types:
            ac_coverage['canteen'].append(school['name'])
            coverage_count += 1
        if 'library' in coverage_types:
            ac_coverage['library'].append(school['name'])
            coverage_count += 1
        
        if coverage_count >= 4:
            ac_coverage['full'].append(school['name'])
        elif coverage_count >= 2:
            ac_coverage['basic'].append(school['name'])

    def render_school_list(schools):
        if not schools:
            return '<li>暂无数据</li>'
        return ''.join([f'<li>{school}</li>' for school in sorted(list(set(schools)))])

    ac_summary_html = f"""
        <h3>🌡️ 空调覆盖情况概览</h3>
        <div class="ac-list">
            <div class="ac-category full">
                <h4>✅ 完全覆盖 ({len(set(ac_coverage['full']))}所)</h4>
                <ul class="ac-schools">{render_school_list(ac_coverage['full'])}</ul>
                <small style="color: #666; font-size: 0.8em;">教室、宿舍、食堂、图书馆四个场所都有空调</small>
            </div>
            <div class="ac-category basic">
                <h4>🆗 基本覆盖 ({len(set(ac_coverage['basic']))}所)</h4>
                <ul class="ac-schools">{render_school_list(ac_coverage['basic'])}</ul>
                <small style="color: #666; font-size: 0.8em;">至少两个主要场所有空调覆盖</small>
            </div>
            <div class="ac-category classroom">
                <h4>🏫 教室有覆盖 ({len(set(ac_coverage['classroom']))}所)</h4>
                <ul class="ac-schools">{render_school_list(ac_coverage['classroom'])}</ul>
            </div>
            <div class="ac-category dormitory">
                <h4>🏠 宿舍有覆盖 ({len(set(ac_coverage['dormitory']))}所)</h4>
                <ul class="ac-schools">{render_school_list(ac_coverage['dormitory'])}</ul>
            </div>
            <div class="ac-category canteen">
                <h4>🍽️ 食堂有覆盖 ({len(set(ac_coverage['canteen']))}所)</h4>
                <ul class="ac-schools">{render_school_list(ac_coverage['canteen'])}</ul>
            </div>
            <div class="ac-category library">
                <h4>📚 图书馆/自习室有覆盖 ({len(set(ac_coverage['library']))}所)</h4>
                <ul class="ac-schools">{render_school_list(ac_coverage['library'])}</ul>
            </div>
            <div class="ac-category none">
                <h4>❌ 完全没有覆盖 ({len(set(ac_coverage['none']))}所)</h4>
                <ul class="ac-schools">{render_school_list(ac_coverage['none'])}</ul>
            </div>
            <div class="ac-category pending">
                <h4>❓ 信息待补充 ({len(set(ac_coverage['pending']))}所)</h4>
                <ul class="ac-schools">{render_school_list(ac_coverage['pending'])}</ul>
            </div>
        </div>
    """

    # 2. 生成贡献部分 HTML
    contribute_html = ""
    if data.get('contribute_links'):
        options_html = ""
        for link in data['contribute_links']:
            btn_class = 'secondary' if link.get('type') != 'github_issue' else ''
            btn_text = '提交 Issue' if link.get('type') == 'github_issue' else '填写问卷'
            options_html += f"""
                <div class="contribute-option">
                    <span class="icon">{link['icon']}</span>
                    <h4>{link['title']}</h4>
                    <p>{link['description']}</p>
                    <div class="update-delay">⏱️ {link['update_delay']}</div>
                    <a href="{link['url']}" class="contribute-btn {btn_class}" target="_blank">
                        {btn_text}
                    </a>
                </div>
            """
        contribute_html = f"""
            <h3>🤝 贡献信息</h3>
            <div class="contribute-options">
                {options_html}
            </div>
        """

    # 3. 生成学校信息 HTML
    schools_html = ""
    for category in data['categories']:
        schools_html += f'<h2 class="category-title">{category["name"]}</h2>'
        for school in category['schools']:
            status_class = f"status-{school.get('status', 'pending')}"
            details_html = ''.join([f"<p>{detail}</p>" for detail in school.get('details', [])])
            schools_html += f"""
                <div class="school">
                    <h3>{school['name']}</h3>
                    <div class="status {status_class}">状态：{school.get('statusText', '')}</div>
                    <div class="school-info">
                        <p>{school.get('description', '')}</p>
                        {details_html}
                    </div>
                </div>
            """

    # 4. 生成介绍部分 HTML
    homepage_link = ''
    if data.get('project_info', {}).get('repository'):
        repo_url = data["project_info"]["repository"]
        homepage_link = f'<p style="text-align: center; margin-top: 15px;"><a href="{repo_url}" target="_blank" style="color: #0366d6; text-decoration: none; font-weight: bold;">🏠 项目首页</a></p>'
    
    intro_html = f"""
        <p><strong>{data['intro']['description']}</strong></p>
        <p>{data['intro']['details']}</p>
        {homepage_link}
    """

    # 5. 生成页脚 HTML
    footer_html = f"""
        <p>{data['footer']['copyright']}</p>
        <p>最后更新时间：{data['footer']['lastUpdate']}</p>
        <p>{data['footer']['tip']}</p>
        <p>{data['footer']['totalCount']}</p>
    """

    # 读取 HTML 模板
    with open('index.html', 'r', encoding='utf-8') as f:
        template = f.read()

    # 替换模板中的占位符
    rendered_html = template
    rendered_html = rendered_html.replace('{{PAGE_TITLE}}', data['title'].replace('🌡️ ', ''))
    rendered_html = rendered_html.replace('{{MAIN_TITLE}}', data['title'])
    rendered_html = rendered_html.replace('{{SUBTITLE}}', data['subtitle'])
    rendered_html = rendered_html.replace('{{INTRO_CONTENT}}', intro_html)
    rendered_html = rendered_html.replace('{{AC_SUMMARY_CONTENT}}', ac_summary_html)
    rendered_html = rendered_html.replace('{{CONTRIBUTE_CONTENT}}', contribute_html)
    rendered_html = rendered_html.replace('{{SCHOOLS_CONTENT}}', schools_html)
    rendered_html = rendered_html.replace('{{FOOTER_CONTENT}}', footer_html)

    # 移除 JS 脚本部分
    rendered_html = re.sub(r'<script>.*?</script>', '', rendered_html, flags=re.DOTALL)

    # 将渲染好的 HTML 写回 index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print("HTML page has been rendered successfully.")

if __name__ == '__main__':
    render_html()
