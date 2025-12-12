import React from "react";

export default function Header({ onOpenDocs }) {
  return (
    <header className="site-header">
      <div className="header-inner">

        <div className="brand">
          <div className="logo">
            <img 
              src="/images/nanthi_icon.JPG"  
              alt="Nanthi Ventures Logo"
              className="logo-img"
            />
          </div>

          <div className="brand-text">
            <div className="brand-title">Nanthi Ventures</div>
            <div className="brand-sub">Applicant Tracking System</div>
          </div>
        </div>

      </div>
    </header>
  );
}
