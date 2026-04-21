"""
Générateur de bulletins de notes PDF — EduPlatform
Utilise ReportLab (Platypus) pour produire un bulletin A4 professionnel.
"""
import io
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, BaseDocTemplate, PageTemplate, Frame
)
from reportlab.lib.colors import HexColor, white, black

# ── Palette ───────────────────────────────────────────────────────────────────
C_NAVY   = HexColor('#0d1b35')
C_BLUE   = HexColor('#1a56db')
C_LIGHT  = HexColor('#dbeafe')
C_ACCENT = HexColor('#f97316')
C_GREEN  = HexColor('#16a34a')
C_RED    = HexColor('#dc2626')
C_YELLOW = HexColor('#b45309')
C_GRAY   = HexColor('#6b7280')
C_LGRAY  = HexColor('#f3f4f6')
C_BORDER = HexColor('#d1d5db')
C_STRIPE = HexColor('#f8fafc')


def grade_color(avg):
    if avg is None: return C_GRAY
    v = float(avg)
    if v >= 16: return C_GREEN
    if v >= 14: return HexColor('#15803d')
    if v >= 12: return C_BLUE
    if v >= 10: return C_YELLOW
    return C_RED


def grade_mention(avg):
    if avg is None: return '—'
    v = float(avg)
    if v >= 16: return 'Très bien'
    if v >= 14: return 'Bien'
    if v >= 12: return 'Assez bien'
    if v >= 10: return 'Passable'
    return 'Insuffisant'


def ordinal_fr(n):
    return '1er' if n == 1 else f'{n}ème'


# ── Style factory ─────────────────────────────────────────────────────────────
def _styles():
    base = getSampleStyleSheet()
    def S(name, **kw):
        return ParagraphStyle(name, parent=base['Normal'], **kw)
    return {
        'school'  : S('school',   fontSize=8,  textColor=C_GRAY,  alignment=TA_CENTER),
        'title'   : S('title',    fontSize=20, textColor=white,   fontName='Helvetica-Bold', alignment=TA_CENTER),
        'sub'     : S('sub',      fontSize=9,  textColor=HexColor('#93c5fd'), alignment=TA_CENTER),
        'field'   : S('field',    fontSize=7.5,textColor=C_GRAY,  fontName='Helvetica'),
        'value'   : S('value',    fontSize=9,  textColor=C_NAVY,  fontName='Helvetica-Bold'),
        'th'      : S('th',       fontSize=7.5,textColor=white,   fontName='Helvetica-Bold', alignment=TA_CENTER),
        'td_c'    : S('td_c',     fontSize=8.5,textColor=C_NAVY,  alignment=TA_CENTER),
        'td_l'    : S('td_l',     fontSize=8.5,textColor=C_NAVY,  alignment=TA_LEFT),
        'mention' : S('mention',  fontSize=7.5,textColor=C_GRAY,  alignment=TA_CENTER, fontName='Helvetica-Oblique'),
        'section' : S('section',  fontSize=9,  textColor=C_NAVY,  fontName='Helvetica-Bold'),
        'footer'  : S('footer',   fontSize=7,  textColor=C_GRAY,  alignment=TA_CENTER),
        'sig'     : S('sig',      fontSize=8.5,textColor=C_NAVY,  alignment=TA_CENTER),
        'ct'      : S('ct',       fontSize=8,  textColor=C_NAVY,  fontName='Helvetica-Bold'),
        'cb'      : S('cb',       fontSize=8.5,textColor=C_NAVY,  alignment=TA_JUSTIFY),
        'stat_v'  : S('stat_v',   fontSize=15, textColor=C_NAVY,  fontName='Helvetica-Bold', alignment=TA_CENTER),
        'stat_l'  : S('stat_l',   fontSize=7,  textColor=C_GRAY,  alignment=TA_CENTER),
        'tot'     : S('tot',      fontSize=9,  textColor=C_NAVY,  fontName='Helvetica-Bold'),
        'tot_c'   : S('tot_c',    fontSize=9,  textColor=C_NAVY,  fontName='Helvetica-Bold', alignment=TA_CENTER),
        'tot_avg' : S('tot_avg',  fontSize=12, fontName='Helvetica-Bold', alignment=TA_CENTER),
    }


def generate_report_card_pdf(report_card):
    """
    Génère le bulletin de notes complet en PDF.
    Retourne un BytesIO.
    """
    from .models import SubjectGrade

    buf = io.BytesIO()
    W, H = A4
    margin = 1.4 * cm
    pw = W - 2 * margin   # usable page width

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin,
        title=f"Bulletin — {report_card.student.get_full_name()}",
        author="EduPlatform",
    )

    St  = _styles()
    rc  = report_card
    tr  = rc.trimester
    cls = rc.classroom
    stu = rc.student

    try:
        st_id = stu.student_profile.student_id
    except Exception:
        st_id = '—'

    dob  = stu.date_of_birth.strftime('%d/%m/%Y') if stu.date_of_birth else '—'
    sgs  = SubjectGrade.objects.filter(
        student=stu, classroom=cls, trimester=tr
    ).select_related('subject').order_by('subject__name')

    story = []

    # ══════════════════════════════════════════════════════════════════════════
    # 1 ▸ EN-TÊTE
    # ══════════════════════════════════════════════════════════════════════════
    hdr = Table([[
        Paragraph(
            "REPUBLIQUE DU BENIN<br/>"
            "<b>Ministère des Enseignements Secondaire</b><br/>"
            "et de la Formation Technique et Professionnelle",
            St['school']),
        Paragraph(
            "<font size='28'>🎓</font>",
            ParagraphStyle('logo', parent=getSampleStyleSheet()['Normal'],
                           fontSize=28, alignment=TA_CENTER)),
        Paragraph(
            "<b>ETABLISSEMENT SCOLAIRE</b><br/>"
            "EduPlatform<br/>"
            "<font color='#6b7280'>Cotonou, Bénin</font>",
            St['school']),
    ]], colWidths=[pw * .35, pw * .30, pw * .35])
    hdr.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 3*mm))

    # ── Bandeau titre ─────────────────────────────────────────────────────────
    banner = Table(
        [[Paragraph('BULLETIN DE NOTES', St['title'])],
         [Paragraph(f'{tr.get_number_display()}  ·  Année scolaire {tr.school_year}', St['sub'])]],
        colWidths=[pw])
    banner.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_NAVY),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ('ROUNDEDCORNERS', [5]),
    ]))
    story.append(banner)
    story.append(Spacer(1, 4*mm))

    # ══════════════════════════════════════════════════════════════════════════
    # 2 ▸ INFOS ÉLÈVE
    # ══════════════════════════════════════════════════════════════════════════
    def info_row(label, val):
        return Table([[
            Paragraph(label, St['field']),
            Paragraph(str(val) if val else '—', St['value']),
        ]], colWidths=[3 * cm, None])

    left_infos  = [info_row(l, v) for l, v in [
        ("Nom & Prénoms",    stu.get_full_name().upper()),
        ("Date de naissance", dob),
        ("N° Matricule",     st_id),
    ]]
    right_infos = [info_row(l, v) for l, v in [
        ("Classe",           cls.name),
        ("Niveau",           cls.level.name),
        ("Effectif classe",  str(rc.class_size or '—')),
    ]]

    def info_block(rows, w):
        inner = []
        for r in rows:
            r.setStyle(TableStyle([
                ('TOPPADDING',    (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            inner.append([r])
        t = Table(inner, colWidths=[w])
        t.setStyle(TableStyle([
            ('TOPPADDING',    (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        return t

    hw = (pw - 4*mm) / 2
    info_tbl = Table([[info_block(left_infos, hw), info_block(right_infos, hw)]],
                     colWidths=[hw, hw])
    info_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_LGRAY),
        ('BOX',           (0,0), (-1,-1), 0.5, C_BORDER),
        ('INNERGRID',     (0,0), (-1,-1), 0.3, C_BORDER),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 9),
        ('RIGHTPADDING',  (0,0), (-1,-1), 9),
        ('ROUNDEDCORNERS', [5]),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 5*mm))

    # ══════════════════════════════════════════════════════════════════════════
    # 3 ▸ TABLEAU DES NOTES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Résultats par matière", St['section']))
    story.append(Spacer(1, 2*mm))

    col_w = [pw*.27, pw*.06, pw*.11, pw*.11, pw*.11, pw*.20, pw*.14]

    header = [
        Paragraph('MATIÈRE',        St['th']),
        Paragraph('COEF',           St['th']),
        Paragraph('MOY./20',        St['th']),
        Paragraph('MOY.×COEF',      St['th']),
        Paragraph('CLASSE MOY.',    St['th']),
        Paragraph('APPRÉCIATION',   St['th']),
        Paragraph('ENSEIGNANT',     St['th']),
    ]
    rows = [header]

    for i, sg in enumerate(sgs):
        avg = sg.average
        wt  = sg.weighted_average
        gc  = grade_color(avg)
        avg_s = f"{float(avg):.2f}" if avg is not None else '—'
        wt_s  = f"{float(wt):.2f}"  if wt  is not None else '—'

        subj_p = Paragraph(
            f'<font color="{sg.subject.color or "#4f9cf9"}">■</font> {sg.subject.name}',
            St['td_l'])
        avg_p = Paragraph(
            f'<b>{avg_s}</b>',
            ParagraphStyle(f'avg{i}', parent=getSampleStyleSheet()['Normal'],
                           fontSize=9, fontName='Helvetica-Bold',
                           alignment=TA_CENTER, textColor=gc))
        rows.append([
            subj_p,
            Paragraph(str(sg.subject.coefficient), St['td_c']),
            avg_p,
            Paragraph(wt_s, St['td_c']),
            Paragraph('—', St['td_c']),
            Paragraph(grade_mention(avg), St['mention']),
            Paragraph((sg.teacher_comment or '—')[:28], St['mention']),
        ])

    # Total row
    gen = rc.general_average
    gen_s = f"{float(gen):.2f}" if gen is not None else '—'
    gen_p = Paragraph(
        f'<b>{gen_s}</b>',
        ParagraphStyle('gen', parent=getSampleStyleSheet()['Normal'],
                       fontSize=13, fontName='Helvetica-Bold',
                       alignment=TA_CENTER, textColor=grade_color(gen)))
    rows.append([
        Paragraph('<b>MOYENNE GÉNÉRALE</b>', St['tot']),
        Paragraph('', St['tot_c']),
        gen_p,
        Paragraph('', St['td_c']),
        Paragraph('', St['td_c']),
        Paragraph(f'<b>{grade_mention(gen)}</b>',
                  ParagraphStyle('gen_m', parent=getSampleStyleSheet()['Normal'],
                                 fontSize=9, fontName='Helvetica-Bold',
                                 alignment=TA_CENTER, textColor=grade_color(gen))),
        Paragraph('', St['td_c']),
    ])

    n = len(rows)
    gt = Table(rows, colWidths=col_w, repeatRows=1)
    gt.setStyle(TableStyle([
        # header
        ('BACKGROUND',    (0,0), (-1,0), C_NAVY),
        ('TOPPADDING',    (0,0), (-1,0), 6),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        # body
        ('TOPPADDING',    (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 5),
        ('RIGHTPADDING',  (0,0), (-1,-1), 5),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID',     (0,0), (-1,-1), 0.25, C_BORDER),
        ('BOX',           (0,0), (-1,-1), 0.8,  C_NAVY),
        # alternating stripes (rows 2, 4, 6…)
        *[('BACKGROUND', (0,i), (-1,i), C_STRIPE) for i in range(2, n-1, 2)],
        # total row
        ('BACKGROUND',    (0, n-1), (-1, n-1), C_LIGHT),
        ('TOPPADDING',    (0, n-1), (-1, n-1), 7),
        ('BOTTOMPADDING', (0, n-1), (-1, n-1), 7),
        ('BOX',           (0, n-1), (-1, n-1), 1.2, C_NAVY),
    ]))
    story.append(gt)
    story.append(Spacer(1, 5*mm))

    # ══════════════════════════════════════════════════════════════════════════
    # 4 ▸ STATISTIQUES
    # ══════════════════════════════════════════════════════════════════════════
    rank_s   = ordinal_fr(rc.rank)           if rc.rank            else '—'
    cl_avg_s = f"{float(rc.class_average):.2f}"   if rc.class_average   else '—'
    hi_s     = f"{float(rc.highest_average):.2f}" if rc.highest_average else '—'
    lo_s     = f"{float(rc.lowest_average):.2f}"  if rc.lowest_average  else '—'
    abs_s    = str(rc.absences_total)
    late_s   = str(rc.lates_total)
    cond_s   = rc.get_conduct_grade_display()

    def stat_cell(label, val, color=C_NAVY):
        t = Table([
            [Paragraph(val,   ParagraphStyle('sv', parent=getSampleStyleSheet()['Normal'],
                               fontSize=14, fontName='Helvetica-Bold',
                               textColor=color, alignment=TA_CENTER))],
            [Paragraph(label, St['stat_l'])],
        ])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), C_LGRAY),
            ('BOX',           (0,0), (-1,-1), 0.4, C_BORDER),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('ROUNDEDCORNERS', [4]),
        ]))
        return t

    cw7 = [pw / 7] * 7
    stats_row = Table([[
        stat_cell("RANG",          rank_s,  C_ACCENT),
        stat_cell("MOY. CLASSE",   cl_avg_s, C_BLUE),
        stat_cell("MEILLEURE",     hi_s,    C_GREEN),
        stat_cell("PLUS BASSE",    lo_s,    C_RED),
        stat_cell("ABSENCES",      abs_s,   C_RED if rc.absences_total > 0 else C_GREEN),
        stat_cell("RETARDS",       late_s,  C_YELLOW if rc.lates_total > 0 else C_GREEN),
        stat_cell("CONDUITE",      cond_s,  C_BLUE),
    ]], colWidths=cw7)
    stats_row.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(stats_row)
    story.append(Spacer(1, 5*mm))

    # ══════════════════════════════════════════════════════════════════════════
    # 5 ▸ COMMENTAIRES
    # ══════════════════════════════════════════════════════════════════════════
    def comment_box(title, text, w):
        t = Table([
            [Paragraph(title, St['ct'])],
            [Paragraph(text or 'Aucune observation.', St['cb'])],
        ], colWidths=[w])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (0,0), C_LIGHT),
            ('BACKGROUND',    (0,1), (0,1), white),
            ('BOX',           (0,0), (-1,-1), 0.5, C_BORDER),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('RIGHTPADDING',  (0,0), (-1,-1), 8),
            ('ROUNDEDCORNERS', [4]),
        ]))
        return t

    comments = Table([[
        comment_box("Appréciation du professeur principal",
                    rc.class_teacher_comment, hw),
        comment_box("Décision du conseil de classe / Direction",
                    rc.principal_comment, hw),
    ]], colWidths=[hw, hw])
    comments.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(comments)
    story.append(Spacer(1, 7*mm))

    # ══════════════════════════════════════════════════════════════════════════
    # 6 ▸ SIGNATURES
    # ══════════════════════════════════════════════════════════════════════════
    sig_text = "\n\n\n\n________________________"
    sig_tbl = Table([[
        Paragraph(f"Le Professeur Principal{sig_text}", St['sig']),
        Paragraph(f"Visa des Parents / Tuteurs{sig_text}", St['sig']),
        Paragraph(f"Le Directeur de l'Établissement{sig_text}", St['sig']),
    ]], colWidths=[pw / 3] * 3)
    sig_tbl.setStyle(TableStyle([
        ('BOX',           (0,0), (-1,-1), 0.5, C_BORDER),
        ('INNERGRID',     (0,0), (-1,-1), 0.3, C_BORDER),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sig_tbl)

    # ── Pied de page ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width=pw, thickness=0.4, color=C_BORDER))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        f"EduPlatform · Bulletin généré le {rc.updated_at.strftime('%d/%m/%Y à %H:%M')} "
        f"· Document officiel non modifiable",
        St['footer']))

    doc.build(story)
    buf.seek(0)
    return buf
