/*  ==========================================================================
    كان يا مكان — Teaser 03 · 7 s · 1080×1920 · 30 fps
    After Effects build script (AE 2022 or newer; AE 2024+ recommended)

    HOW TO RUN
      1. Install the fonts: Reem Kufi (Regular + SemiBold) from Google Fonts.
      2. Preferences › Type › Text Engine Options › "South Asian and Middle
         Eastern", then restart AE. (Without it Arabic will not join.)
      3. Put your master logo next to this script as  assets/kan-logo.png
         (transparent PNG, or kan-logo.ai). If it is missing, the script uses
         assets/kan-logo-trace.png (a vector trace) and warns you.
      4. File › Scripts › Run Script File… › choose this file.

    WHAT IT BUILDS (honest scope)
      • The full 7-second composition, every layer named, keyed and eased.
      • The morph is a glyph choreography of real, correctly shaped Arabic
        forms (zero-width joiner pieces): the meem travels, the alef lifts
        out, the gap closes, and the kaf cuts from its initial to its medial
        form on the frame of contact. Letters are never stretched.
      • It does NOT vertex-morph letter outlines (AE interpolates mismatched
        glyph paths badly). The optional connector draw-on is described in
        the canvas build guide.
    ========================================================================== */

(function KanYaMakanBuild() {

    // ---------- settings --------------------------------------------------
    var W = 1080, H = 1920, FPS = 30, DUR = 7;
    var HERO_FONTS   = ["ReemKufi-SemiBold", "ReemKufi-Bold", "ReemKufi-Medium", "ReemKufi-Regular", "NotoKufiArabic-SemiBold", "NotoKufiArabic-Bold"];
    var SLOGAN_FONTS = ["ReemKufi-Regular", "ReemKufi-Medium", "NotoKufiArabic-Regular"];
    var HERO_SIZE = 120, SLOGAN_SIZE = 48;
    var WORD_GAP = 36;          // px between words
    var JOIN_OVERLAP = 1.5;     // px overlap at cursive joins (hides hairlines)
    var DOT = 14;               // diamond square size (the logo's noon dot)
    var DOT_SLOT = 20, DOT_GAP = 8, DOT_LEAD = 8;
    var HERO_Y = 960, HERO_Y_END = 880;   // optical centre of the hero line
    var BASELINE = 36;          // baseline sits this far below the optical centre
    var RULE_Y = 1052, RULE_LEN = 180, RULE_ANGLE = -12.7;
    var SLOGAN_Y = 1130;
    var LOGO_TOP = 1272, LOGO_W = 280;

    var SCRIPT_FOLDER = File($.fileName).parent;
    var warnings = [];

    function hex(h) { return [parseInt(h.substr(1, 2), 16) / 255, parseInt(h.substr(3, 2), 16) / 255, parseInt(h.substr(5, 2), 16) / 255]; }
    var C = { brown: hex("#391D15"), vig: hex("#1E0E09"), sand: hex("#D2B48C"), soft: hex("#C4A881"), hi: hex("#F0DDBE"), copper: hex("#E3976E"), grey: [0.5, 0.5, 0.5] };

    var ZWJ = "‍";
    var TXT = {
        kan:    "كان",                 // كان
        ya:     "يا",                       // يا
        meem:   "م" + ZWJ,                       // مـ  (initial form)
        alef:   ZWJ + "ا",                       // ـا  (final form)
        kanMed: ZWJ + "كان",           // ـكان (medial kaf)
        slogan: "هالمرة الحكاية إلها مكان." // هالمرة الحكاية إلها مكان.
    };

    // ---------- helpers ---------------------------------------------------
    function sec(frame) { return frame / FPS; }

    function padTo(prop, v) {
        if (!(v instanceof Array)) return v;
        var cur = prop.value;
        if (cur instanceof Array && v.length < cur.length) {
            var o = v.slice(0);
            while (o.length < cur.length) o.push(cur[o.length]);
            return o;
        }
        return v;
    }

    function easeDims(prop) {
        var t = prop.propertyValueType;
        if (t === PropertyValueType.TwoD_SPATIAL || t === PropertyValueType.ThreeD_SPATIAL ||
            t === PropertyValueType.SHAPE || t === PropertyValueType.OneD || t === PropertyValueType.COLOR) return 1;
        return (prop.value instanceof Array) ? prop.value.length : 1;
    }

    // key(prop, frame, value, inInfluence, outInfluence, hold)
    function key(prop, frame, val, inInf, outInf, hold) {
        var i = prop.addKey(sec(frame));
        prop.setValueAtKey(i, padTo(prop, val));
        var n = easeDims(prop), ein = [], eout = [], a = (inInf == null ? 33.33 : inInf), b = (outInf == null ? 33.33 : outInf);
        for (var d = 0; d < n; d++) { ein.push(new KeyframeEase(0, Math.max(0.1, a))); eout.push(new KeyframeEase(0, Math.max(0.1, b))); }
        try { prop.setTemporalEaseAtKey(i, ein, eout); }
        catch (e) { try { prop.setTemporalEaseAtKey(i, [ein[0]], [eout[0]]); } catch (e2) {} }
        if (hold) { try { prop.setInterpolationTypeAtKey(i, KeyframeInterpolationType.HOLD); } catch (e3) {} }
        if (prop.isSpatial) {
            try {
                prop.setSpatialAutoBezierAtKey(i, false);
                prop.setSpatialContinuousAtKey(i, false);
                var z = []; for (var q = 0; q < prop.value.length; q++) z.push(0);
                prop.setSpatialTangentsAtKey(i, z, z);           // straight motion paths, no overshoot
            } catch (e4) {}
        }
        return i;
    }

    function tr(layer, name) { return layer.property("ADBE Transform Group").property(name); }
    function set(prop, v) { prop.setValue(padTo(prop, v)); }
    function addFx(layer, match) { return layer.property("ADBE Effect Parade").addProperty(match); }
    function fxProp(effect, matchName, displayName) {
        try { var p = effect.property(matchName); if (p) return p; } catch (e) {}
        try { return effect.property(displayName); } catch (e2) { return null; }
    }
    function trySet(effect, names, v) {
        for (var i = 0; i < names.length; i++) { try { var p = effect.property(names[i]); if (p) { p.setValue(v); return true; } } catch (e) {} }
        return false;
    }
    function rect(l, t, r, b) { var s = new Shape(); s.vertices = [[l, t], [r, t], [r, b], [l, b]]; s.closed = true; return s; }
    function ellipse(cx, cy, rx, ry) {
        var k = 0.5523, s = new Shape();
        s.vertices = [[cx, cy - ry], [cx + rx, cy], [cx, cy + ry], [cx - rx, cy]];
        s.inTangents  = [[-rx * k, 0], [0, -ry * k], [rx * k, 0], [0, ry * k]];
        s.outTangents = [[rx * k, 0], [0, ry * k], [-rx * k, 0], [0, -ry * k]];
        s.closed = true; return s;
    }

    function makeText(comp, name, str, fonts, size, color) {
        var layer = comp.layers.addText(str);
        layer.name = name;
        var prop = layer.property("ADBE Text Properties").property("ADBE Text Document");
        var used = null;
        for (var i = 0; i < fonts.length && !used; i++) {
            var td = prop.value;
            try { td.resetCharStyle(); td.resetParagraphStyle(); } catch (e0) {}
            td.font = fonts[i];
            td.fontSize = size;
            td.applyFill = true; td.fillColor = color;
            td.applyStroke = false;
            td.tracking = 0;                                   // never track connected Arabic
            td.justification = ParagraphJustification.CENTER_JUSTIFY;
            try { td.direction = ParagraphDirection.DIRECTION_RIGHT_TO_LEFT; } catch (e1) {}
            prop.setValue(td);
            if (prop.value.font === fonts[i]) used = fonts[i];
        }
        if (!used) warnings.push("Font missing for " + name + " (tried " + fonts.join(", ") + "). Install Reem Kufi and re-run.");
        try {
            if (prop.value.composerEngine === ComposerEngine.LATIN_CJK_ENGINE && warnings.join().indexOf("Text engine") < 0)
                warnings.push("Text engine is Latin/CJK: Arabic will not join. Preferences › Type › South Asian and Middle Eastern, restart AE, re-run.");
        } catch (e2) {}
        layer.motionBlur = true;
        return layer;
    }

    // anchor = horizontal centre of the ink box, vertical = baseline
    function anchorBaseline(layer) {
        var r = layer.sourceRectAtTime(0, false);
        set(tr(layer, "ADBE Anchor Point"), [r.left + r.width / 2, 0]);
        return { w: r.width, rect: r };
    }

    function revealMask(layer, s0, dur) {
        var r = layer.sourceRectAtTime(0, false);
        var L = r.left - 70, R = r.left + r.width + 70, T = r.top - 90, B = r.top + r.height + 90;
        var m = layer.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
        m.name = "RTL wipe";
        m.property("ADBE Mask Feather").setValue([60, 60]);
        var p = m.property("ADBE Mask Shape");
        key(p, s0, rect(R - 1, T, R, B), null, 33);            // collapsed on the right edge
        key(p, s0 + dur, rect(L, T, R, B), 85, 33);             // opens leftward (RTL)
    }

    // standard reveal: opacity, rise, blur, RTL mask
    function reveal(layer, s0, x, y) {
        var op = tr(layer, "ADBE Opacity");
        key(op, 0, 0, null, 33, true);
        key(op, s0, 0, null, 33);
        key(op, s0 + 18, 100, 85, 33);
        var pos = tr(layer, "ADBE Position");
        key(pos, s0, [x, y + 14], null, 33);
        key(pos, s0 + 30, [x, y], 85, 33);
        var blur = addFx(layer, "ADBE Gaussian Blur 2");
        var bp = fxProp(blur, "ADBE Gaussian Blur 2-0001", "Blurriness");
        key(bp, s0, 10, null, 33);
        key(bp, s0 + 30, 0, 85, 33);
        revealMask(layer, s0, 30);
        return { op: op, pos: pos, blur: bp };
    }

    // right-to-left layout: items [{w, gapAfter}] → centre x of each, line centred on 0
    function layoutRTL(items) {
        var total = 0, i;
        for (i = 0; i < items.length; i++) total += items[i].w + (i < items.length - 1 ? items[i].gapAfter : 0);
        var cursor = total / 2, xs = [];
        for (i = 0; i < items.length; i++) { xs.push(cursor - items[i].w / 2); cursor -= items[i].w + items[i].gapAfter; }
        return xs;
    }

    function makeDiamond(comp, name, color) {
        var l = comp.layers.addShape();
        l.name = name;
        var g = l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        g.name = "diamond";
        var v = g.property("ADBE Vectors Group");
        var rc = v.addProperty("ADBE Vector Shape - Rect");
        rc.property("ADBE Vector Rect Size").setValue([DOT, DOT]);
        var fill = v.addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        set(tr(l, "ADBE Anchor Point"), [0, 0]);
        tr(l, "ADBE Rotate Z").setValue(45);
        l.motionBlur = true;
        return { layer: l, fill: fill.property("ADBE Vector Fill Color") };
    }

    // ---------- build -----------------------------------------------------
    app.beginUndoGroup("Build — Kan Ya Makan Teaser 03");
    if (!app.project) app.newProject();
    var proj = app.project;

    var folder = proj.items.addFolder("KYM_Teaser03");
    var comp = proj.items.addComp("KYM_Teaser03_1080x1920_30p", W, H, 1, DUR, FPS);
    comp.parentFolder = folder;
    comp.bgColor = C.brown;
    comp.motionBlur = true;
    comp.shutterAngle = 180;
    comp.shutterPhase = -90;
    try { comp.motionBlurSamplesPerFrame = 16; comp.motionBlurAdaptiveSampleLimit = 64; } catch (eMB) {}

    // --- ground (bottom up) ---
    var bg = comp.layers.addSolid(C.brown, "BG_brown", W, H, 1, DUR);
    bg.locked = false;

    var grain = comp.layers.addSolid(C.grey, "BG_grain", W, H, 1, DUR);
    var fn = addFx(grain, "ADBE Fractal Noise");
    trySet(fn, ["Contrast"], 120);
    trySet(fn, ["Complexity"], 6);
    trySet(fn, ["Scale"], 50);
    grain.blendingMode = BlendingMode.OVERLAY;
    tr(grain, "ADBE Opacity").setValue(4);

    var vig = comp.layers.addSolid(C.vig, "BG_vignette", W, H, 1, DUR);
    var vm = vig.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
    vm.property("ADBE Mask Shape").setValue(ellipse(W / 2, H * 0.46, W * 0.62, H * 0.5));
    vm.property("ADBE Mask Feather").setValue([700, 700]);
    vm.inverted = true;
    tr(vig, "ADBE Opacity").setValue(35);

    var frame = comp.layers.addShape();
    frame.name = "FRAME_line";
    var fg = frame.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
    var fv = fg.property("ADBE Vectors Group");
    fv.addProperty("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size").setValue([W - 72, H - 72]);
    var fst = fv.addProperty("ADBE Vector Graphic - Stroke");
    fst.property("ADBE Vector Stroke Color").setValue(C.sand);
    fst.property("ADBE Vector Stroke Width").setValue(1.5);
    set(tr(frame, "ADBE Anchor Point"), [0, 0]);
    set(tr(frame, "ADBE Position"), [W / 2, H / 2]);
    key(tr(frame, "ADBE Opacity"), 0, 0, null, 33);
    key(tr(frame, "ADBE Opacity"), 30, 28, 85, 33);

    // --- hero parent ---
    var hero = comp.layers.addNull(DUR);
    hero.name = "HERO_NULL";
    set(tr(hero, "ADBE Anchor Point"), [0, 0]);
    set(tr(hero, "ADBE Position"), [W / 2, HERO_Y]);
    key(tr(hero, "ADBE Position"), 122, [W / 2, HERO_Y], null, 40);
    key(tr(hero, "ADBE Position"), 150, [W / 2, HERO_Y_END], 90, 33);

    // --- hero pieces (created, measured, then laid out) ---
    var L = {
        w1:  makeText(comp, "W1", TXT.kan, HERO_FONTS, HERO_SIZE, C.sand),
        w2:  makeText(comp, "W2", TXT.ya, HERO_FONTS, HERO_SIZE, C.sand),
        m:   makeText(comp, "W3_meem", TXT.meem, HERO_FONTS, HERO_SIZE, C.sand),
        a:   makeText(comp, "W3_alef", TXT.alef, HERO_FONTS, HERO_SIZE, C.sand),
        k1:  makeText(comp, "W4_kaf_initial", TXT.kan, HERO_FONTS, HERO_SIZE, C.sand),
        k2:  makeText(comp, "W4_kaf_medial", TXT.kanMed, HERO_FONTS, HERO_SIZE, C.sand)
    };
    var Wd = {};
    for (var nm in L) { if (L.hasOwnProperty(nm)) Wd[nm] = anchorBaseline(L[nm]).w; }

    var d1 = makeDiamond(comp, "DOT_1", C.sand);
    var d2 = makeDiamond(comp, "DOT_2", C.sand);
    var d3 = makeDiamond(comp, "DOT_3", C.sand);

    for (nm in L) { if (L.hasOwnProperty(nm)) L[nm].parent = hero; }
    d1.layer.parent = hero; d2.layer.parent = hero; d3.layer.parent = hero;

    // layout A: كان يا ما كان...
    var A = layoutRTL([
        { w: Wd.w1, gapAfter: WORD_GAP }, { w: Wd.w2, gapAfter: WORD_GAP },
        { w: Wd.m,  gapAfter: -JOIN_OVERLAP }, { w: Wd.a, gapAfter: WORD_GAP },
        { w: Wd.k1, gapAfter: DOT_LEAD },
        { w: DOT_SLOT, gapAfter: DOT_GAP }, { w: DOT_SLOT, gapAfter: DOT_GAP }, { w: DOT_SLOT, gapAfter: 0 }
    ]);
    // layout B: كان يا مكان.
    var B = layoutRTL([
        { w: Wd.w1, gapAfter: WORD_GAP }, { w: Wd.w2, gapAfter: WORD_GAP },
        { w: Wd.m,  gapAfter: -JOIN_OVERLAP }, { w: Wd.k2, gapAfter: DOT_LEAD },
        { w: DOT_SLOT, gapAfter: 0 }
    ]);
    var kOff = (Wd.k2 - Wd.k1) / 2;          // medial kaf shares the initial kaf's left edge
    var k1B = B[3] - kOff;
    var Y = BASELINE, DOT_Y = BASELINE - DOT * 0.71 - 2;

    // phase 1 — reveals (8-frame stagger, right to left)
    var rW1 = reveal(L.w1, 6,  A[0], Y);
    var rW2 = reveal(L.w2, 14, A[1], Y);
    var rM  = reveal(L.m,  22, A[2], Y);
    var rA  = reveal(L.a,  26, A[3], Y);
    var rK1 = reveal(L.k1, 30, A[4], Y);

    // phase 2 — the morph
    function slide(pos, xA, xB) { key(pos, 70, [xA, Y], 33, 70); key(pos, 102, [xB, Y], 85, 33); }
    slide(rW1.pos, A[0], B[0]);
    slide(rW2.pos, A[1], B[1]);
    slide(rM.pos,  A[2], B[2]);
    slide(rK1.pos, A[4], k1B);

    // meem: copper flag, then back to sand
    var mFill = addFx(L.m, "ADBE Fill");
    var mCol = fxProp(mFill, "ADBE Fill-0002", "Color");
    key(mCol, 60, C.sand, null, 33); key(mCol, 70, C.copper, 85, 33);
    key(mCol, 102, C.copper, null, 33); key(mCol, 110, C.sand, 85, 33);

    // alef: flag, dip, lift, narrow, blur, fade — x follows the meem
    var aFill = addFx(L.a, "ADBE Fill");
    var aCol = fxProp(aFill, "ADBE Fill-0002", "Color");
    key(aCol, 60, C.sand, null, 33); key(aCol, 70, C.copper, 85, 33);
    key(rA.pos, 60, [A[3], Y], null, 33);
    key(rA.pos, 66, [A[3], Y + 6], 70, 33);
    key(rA.pos, 94, [A[3], Y - 92], 90, 33);
    tr(L.a, "ADBE Position").expression =
        "// alef stays attached to the meem\nvar m = thisComp.layer(\"W3_meem\").transform.position;\n[m[0] + (" + (A[3] - A[2]).toFixed(2) + "), value[1]];";
    var aSc = tr(L.a, "ADBE Scale");
    key(aSc, 68, [100, 100], null, 33); key(aSc, 94, [65, 112], 90, 33);
    key(rA.op, 72, 100, null, 33); key(rA.op, 92, 0, 85, 33);
    key(rA.blur, 72, 0, null, 33); key(rA.blur, 94, 14, 85, 33);

    // kaf: initial → medial at the frame of contact
    key(rK1.op, 95, 100, null, 33); key(rK1.op, 101, 0, 33, 33);
    var k2op = tr(L.k2, "ADBE Opacity");
    key(k2op, 0, 0, null, 33, true); key(k2op, 95, 0, null, 33); key(k2op, 101, 100, 33, 33);
    tr(L.k2, "ADBE Position").expression =
        "// medial kaf rides on the initial kaf, left edges aligned\nvar k = thisComp.layer(\"W4_kaf_initial\").transform.position;\n[k[0] + (" + kOff.toFixed(2) + "), k[1]];";

    // dots: in, travel, drop / brighten + pulse
    function dotIn(d, s0) {
        var op = tr(d.layer, "ADBE Opacity"), sc = tr(d.layer, "ADBE Scale");
        key(op, 0, 0, null, 33, true); key(op, s0, 0, null, 33); key(op, s0 + 12, 100, 85, 33);
        key(sc, s0, [40, 40], null, 33); key(sc, s0 + 12, [100, 100], 85, 33);
        return { op: op, sc: sc };
    }
    var dd1 = dotIn(d1, 46), dd2 = dotIn(d2, 51), dd3 = dotIn(d3, 56);
    var d1pos = tr(d1.layer, "ADBE Position");
    set(d1pos, [A[5], DOT_Y]);
    key(d1pos, 70, [A[5], DOT_Y], 33, 70); key(d1pos, 102, [B[4], DOT_Y], 85, 33);
    key(d1.fill, 96, C.sand, null, 33); key(d1.fill, 112, C.hi, 85, 33);
    key(dd1.sc, 100, [100, 100], null, 50); key(dd1.sc, 107, [140, 140], 60, 60); key(dd1.sc, 114, [100, 100], 85, 33);

    function dotDrop(d, dd, xA, drop) {
        var p = tr(d.layer, "ADBE Position");
        set(p, [xA, DOT_Y]);
        key(p, 80, [xA, DOT_Y], null, 33); key(p, 98, [xA, DOT_Y + drop], 85, 33);
        p.expression = "// follows DOT_1 horizontally\nvar d = thisComp.layer(\"DOT_1\").transform.position;\n[d[0] + (" + (xA - A[5]).toFixed(2) + "), value[1]];";
        key(dd.op, 80, 100, null, 33); key(dd.op, 98, 0, 85, 33);
    }
    dotDrop(d2, dd2, A[6], 24);
    dotDrop(d3, dd3, A[7], 28);

    // phase 3 — rule (the logo's fatha stroke)
    var rule = comp.layers.addShape();
    rule.name = "RULE_fatha";
    var rg = rule.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
    var rv = rg.property("ADBE Vectors Group");
    var path = rv.addProperty("ADBE Vector Shape - Group");
    var ln = new Shape(); ln.vertices = [[RULE_LEN / 2, 0], [-RULE_LEN / 2, 0]]; ln.closed = false;   // starts on the right
    path.property("ADBE Vector Shape").setValue(ln);
    var rs = rv.addProperty("ADBE Vector Graphic - Stroke");
    rs.property("ADBE Vector Stroke Color").setValue(C.sand);
    rs.property("ADBE Vector Stroke Width").setValue(3);
    try { rs.property("ADBE Vector Stroke Line Cap").setValue(2); } catch (eCap) {}
    var trim = rg.property("ADBE Vectors Group").addProperty("ADBE Vector Filter - Trim");
    set(tr(rule, "ADBE Anchor Point"), [0, 0]);
    set(tr(rule, "ADBE Position"), [W / 2, RULE_Y]);
    tr(rule, "ADBE Rotate Z").setValue(RULE_ANGLE);
    var te = trim.property("ADBE Vector Trim End");
    key(te, 138, 0, null, 33); key(te, 166, 100, 90, 33);
    key(tr(rule, "ADBE Opacity"), 138, 0, null, 33); key(tr(rule, "ADBE Opacity"), 146, 100, 85, 33);

    // slogan
    var slogan = makeText(comp, "SLOGAN", TXT.slogan, SLOGAN_FONTS, SLOGAN_SIZE, C.soft);
    anchorBaseline(slogan);
    var sy = SLOGAN_Y + Math.round(SLOGAN_SIZE * 0.3);
    var sop = tr(slogan, "ADBE Opacity"), spos = tr(slogan, "ADBE Position");
    key(sop, 0, 0, null, 33, true); key(sop, 146, 0, null, 33); key(sop, 170, 100, 85, 33);
    key(spos, 146, [W / 2, sy + 24], null, 33); key(spos, 180, [W / 2, sy], 90, 33);
    var sb = fxProp(addFx(slogan, "ADBE Gaussian Blur 2"), "ADBE Gaussian Blur 2-0001", "Blurriness");
    key(sb, 146, 8, null, 33); key(sb, 180, 0, 90, 33);

    // logo
    var logoFile = null, candidates = ["assets/kan-logo.png", "assets/kan-logo.ai", "assets/kan-logo.psd", "assets/kan-logo-trace.png"];
    for (var c = 0; c < candidates.length && !logoFile; c++) {
        var fl = new File(SCRIPT_FOLDER.fsName + "/" + candidates[c]);
        if (fl.exists) logoFile = fl;
    }
    var logo;
    if (logoFile) {
        var io = new ImportOptions(logoFile);
        var item = proj.importFile(io);
        item.parentFolder = folder;
        logo = comp.layers.add(item);
        logo.name = "LOGO";
        if (logoFile.name.indexOf("trace") >= 0) warnings.push("Using the logo TRACE. Drop the master file in assets/kan-logo.png and re-run (or Alt-drag it onto the LOGO layer).");
        var sc = LOGO_W / item.width * 100;
        var lh = item.height * sc / 100;
        set(tr(logo, "ADBE Position"), [W / 2, LOGO_TOP + lh / 2]);
        var lsc = tr(logo, "ADBE Scale");
        key(lsc, 170, [sc * 0.96, sc * 0.96], null, 33); key(lsc, 196, [sc, sc], 90, 33);
        var lpos = tr(logo, "ADBE Position");
        key(lpos, 170, [W / 2, LOGO_TOP + lh / 2 + 12], null, 33); key(lpos, 196, [W / 2, LOGO_TOP + lh / 2], 90, 33);
    } else {
        logo = comp.layers.addShape();
        logo.name = "LOGO_PLACEHOLDER — Alt-drag your logo onto me";
        var pg = logo.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        var pv = pg.property("ADBE Vectors Group");
        pv.addProperty("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size").setValue([LOGO_W, 262]);
        var ps = pv.addProperty("ADBE Vector Graphic - Stroke");
        ps.property("ADBE Vector Stroke Color").setValue(C.sand);
        ps.property("ADBE Vector Stroke Width").setValue(2);
        set(tr(logo, "ADBE Anchor Point"), [0, 0]);
        set(tr(logo, "ADBE Position"), [W / 2, LOGO_TOP + 131]);
        warnings.push("No logo file found in assets/. A placeholder was created.");
    }
    logo.motionBlur = true;
    var lop = tr(logo, "ADBE Opacity");
    key(lop, 0, 0, null, 33, true); key(lop, 170, 0, null, 33); key(lop, 190, 100, 85, 33);

    // ---------- markers: phases + sound cues -----------------------------
    var mk = comp.markerProperty;
    function marker(frame, text, durFrames) {
        var mv = new MarkerValue(text);
        if (durFrames) mv.duration = sec(durFrames);
        mk.setValueAtTime(sec(frame), mv);
    }
    marker(0,   "01 THE ORIGINAL STORY · SFX ambience fades in", 60);
    marker(6,   "SFX pen stroke · W1");
    marker(14,  "SFX pen stroke · W2");
    marker(22,  "SFX pen stroke · W3");
    marker(30,  "SFX pen stroke · W4");
    marker(58,  "SFX inhale / reverse swell", 10);
    marker(60,  "02 THE TRANSFORMATION", 60);
    marker(68,  "SFX airy whoosh, pan R→L", 32);
    marker(98,  "SFX ink tap · contact");
    marker(120, "03 THE FINAL REVEAL", 90);
    marker(146, "SFX single oud harmonic / soft chime");
    marker(170, "SFX logo tone (low, warm)");

    // ---------- render queue ---------------------------------------------
    try {
        var rq = proj.renderQueue.items.add(comp);
        var om = rq.outputModule(1);
        var templates = ["H.264 - Match Render Settings - 15 Mbps", "H.264 - Match Render Settings - 40 Mbps", "High Quality with Alpha", "High Quality"];
        for (var t = 0; t < templates.length; t++) { try { om.applyTemplate(templates[t]); break; } catch (eT) {} }
        var outFolder = new Folder(SCRIPT_FOLDER.fsName + "/renders");
        if (!outFolder.exists) outFolder.create();
        om.file = new File(outFolder.fsName + "/KYM_Teaser03_1080x1920_30p");
    } catch (eRQ) { warnings.push("Render queue not set: " + eRQ.toString()); }

    comp.openInViewer();
    app.endUndoGroup();

    alert("كان يا مكان — Teaser 03 built.\n\n" +
          "Comp: KYM_Teaser03_1080x1920_30p (7 s, 30 fps)\n" +
          "Layers: hero pieces, 3 diamond dots, fatha rule, slogan, logo, ground.\n" +
          "Markers carry every sound cue.\n" +
          (warnings.length ? "\nCHECK:\n• " + warnings.join("\n• ") : "\nNo warnings."));
})();
