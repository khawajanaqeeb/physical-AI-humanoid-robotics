/**
 * Custom Navbar Item for Login/Logout functionality
 */
import React from 'react';
import { useNavbarItem } from '@docusaurus/theme-common/internal';
import SimpleLoginLogout from '@site/src/components/auth/SimpleLoginLogout';

function LoginLogoutNavbarItem({}) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', height: 'var(--ifm-navbar-height)' }}>
      <SimpleLoginLogout />
    </div>
  );
}

export default LoginLogoutNavbarItem;