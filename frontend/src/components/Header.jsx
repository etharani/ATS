import React from "react";

export default function Header({ onOpenDocs }) {
  return (
    <header className="site-header">
      <div className="header-inner">
        <div className="brand">
          <div className="logo" aria-hidden>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="1" width="22" height="22" rx="6" fill="#15a2deff"/>
              <path d="M6 15.5L10 9l4 6.5 3-4" stroke="#fdfbfaff" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="brand-text">
            <div className="brand-title">Simple ATS</div>
            <div className="brand-sub">Resume ranking & quick previews</div>
          </div>
        </div>
      </div>
    </header>
  );
}
