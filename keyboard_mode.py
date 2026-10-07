# -*- coding: utf-8 -*-
"""키보드 모드: 숫자 1~4로 보기 선택, ←/→로 이전·다음, Enter로 제출·확인·다음 문제,
Space로 카드 뒤집기, O/X로 OX 퀴즈 답하기.

license_quiz의 키보드 모드를 옮긴 것이다. st.html은 iframe 없이 페이지에 바로 들어가므로
부모 문서에 스크립트를 심는 우회 없이 리스너를 한 번만 등록하고, 켜짐 여부만 매번 갱신한다.
마우스 모드에서는 리스너가 아무 동작도 하지 않아 터치 기기와 충돌하지 않는다.
"""
import streamlit as st

_SCRIPT = """
<script>
(function () {
  window.__kbdModeOn = __ENABLED__;
  if (window.__kbdListenerAdded) return;
  window.__kbdListenerAdded = true;

  // 버튼 글자에서 Material 아이콘 이름(예: arrow_forward)을 빼고 실제 라벨만 꺼낸다.
  function label(btn) {
    var clone = btn.cloneNode(true);
    clone.querySelectorAll('[data-testid="stIconMaterial"]').forEach(function (i) { i.remove(); });
    return clone.textContent.trim();
  }
  // 접힌 탭·익스팬더 안처럼 그려지지 않은 요소만 뺀다. 화면 밖으로 스크롤된 버튼도 눌려야 한다.
  function visible(el) {
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function nearestToCenter(els) {
    var mid = window.innerHeight / 2, best = null, bestDist = Infinity;
    els.forEach(function (el) {
      var r = el.getBoundingClientRect();
      var d = Math.abs((r.top + r.bottom) / 2 - mid);
      if (d < bestDist) { bestDist = d; best = el; }
    });
    return best;
  }
  function findButton(labels, exact) {
    var btns = Array.from(document.querySelectorAll('button')).filter(function (b) {
      if (b.disabled || !visible(b)) return false;
      var t = label(b);
      return labels.some(function (w) { return exact ? t === w : t.indexOf(w) === 0; });
    });
    return nearestToCenter(btns);
  }
  function click(el, e) {
    if (!el) return;
    el.click();
    e.preventDefault();
    e.stopPropagation();
  }

  var CHOICE = { '1': 0, '2': 1, '3': 2, '4': 3 };

  document.addEventListener('keydown', function (e) {
    if (!window.__kbdModeOn || e.ctrlKey || e.metaKey || e.altKey) return;
    var a = document.activeElement;
    var typing = a && (a.tagName === 'TEXTAREA' || a.isContentEditable ||
      (a.tagName === 'INPUT' && ['radio', 'checkbox', 'button', 'submit'].indexOf((a.type || '').toLowerCase()) === -1));
    if (typing) return;  // 글자 입력 중에는 단축키를 쓰지 않는다(Enter는 폼이 알아서 제출).
    if (a && a.getAttribute('role') === 'slider') return;  // 슬라이더의 ←/→ 조작을 가로채지 않는다.

    if (e.key === 'Enter') {
      // 한 번에 풀기의 '채점하기'는 실수로 시험 전체를 제출하지 않도록 일부러 넣지 않는다.
      return click(findButton(['제출', '확인', '다음 문제', '결과 보기'], true), e);
    }
    if (e.key === 'ArrowRight') return click(findButton(['다음'], false), e);
    if (e.key === 'ArrowLeft') return click(findButton(['이전'], false), e);
    if (e.key === ' ') return click(findButton(['정답 보기', '다시 가리기'], true), e);
    if (e.key === 'o' || e.key === 'O') return click(findButton(['O 맞아요'], true), e);
    if (e.key === 'x' || e.key === 'X') return click(findButton(['X 아니에요'], true), e);

    var idx = CHOICE[e.key];
    if (idx === undefined) return;
    var groups = Array.from(document.querySelectorAll('div[role="radiogroup"]')).filter(function (g) {
      var name = g.getAttribute('aria-label') || '';
      return name.slice(-2) === '보기' && visible(g);
    });
    var target = nearestToCenter(groups);
    if (!target) return;
    var inputs = target.querySelectorAll('input[type="radio"]');
    if (inputs[idx] && !inputs[idx].disabled) {
      inputs[idx].click();
      inputs[idx].blur();
      e.preventDefault();
      e.stopPropagation();
    }
  }, true);
})();
</script>
"""

HELP = (
    "키보드 모드: 숫자 1~4로 보기 선택 · Enter로 제출/확인/다음 문제 · ←/→로 이전/다음 · "
    "개념 카드에서 Space로 뒤집기, O/X로 OX 답하기. "
    "터치 기기와 충돌하지 않도록 기본값은 마우스 모드예요."
)


def inject(enabled):
    st.html(_SCRIPT.replace("__ENABLED__", "true" if enabled else "false"), unsafe_allow_javascript=True)
