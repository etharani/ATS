import React from "react";
import {
  FiDownload,
  FiHelpCircle,
  FiFacebook,
  FiInstagram,
  FiTwitter,
  FiLinkedin,
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

            <a href="#" className="footer-social" title="Facebook">
              <FiFacebook size={20} />
            </a>

            <a href="#" className="footer-social" title="Instagram">
              <FiInstagram size={20} />
            </a>

            <a href="#" className="footer-social" title="Twitter / X">
              <FiTwitter size={20} />
            </a>

            <a href="#" className="footer-social" title="LinkedIn">
              <FiLinkedin size={20} />
            </a>

          </div>

        </div>
      </div>
    </footer>
  );
}
