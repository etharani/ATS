import React from "react";
import {
  FiDownload,
  FiHelpCircle,
  FiFacebook,
  FiInstagram,
  FiTwitter,
  FiLinkedin,
  FiSearch,
} from "react-icons/fi";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="site-footer ">
      <div className="footer-inner">

        {/* Left */}
        <div className="footer-left">
          <small>© {year} Simple ATS • All Rights Reserved</small>
        </div>

        {/* Right */}
        <div className="footer-right">

          {/* Export + Help */}
          <a
            href="#"
            className="footer-link"
            onClick={(e) => {
              e.preventDefault();
              alert("Export CSV coming soon");
            }}
          >
            <FiDownload size={16} />
            Export CSV
          </a>

          <span className="sep">•</span>

          <a
            href="#"
            className="footer-link"
            onClick={(e) => {
              e.preventDefault();
              alert("Help coming soon");
            }}
          >
            <FiHelpCircle size={16} />
            Help
          </a>

          {/* Social Icons */}
          <span className="sep">•</span>

          <div className="social-icons">

            <a
              href="https://nanthiventures.com/"
              className="footer-social"
              title="Website"
              target="_blank"
              rel="noopener noreferrer"
            >
              <FiSearch size={20} />
            </a>

            <a
              href="https://www.linkedin.com/company/nanthiventures/"
              className="footer-social"
              title="LinkedIn"
              target="_blank"
              rel="noopener noreferrer"
            >
              <FiLinkedin size={20} />
            </a>

          </div>

        </div>
      </div>
    </footer>
  );
}
