/**
 * Custom Navbar Item Component Types
 *
 * This file registers custom navbar item types with Docusaurus.
 * When you use type: 'custom-XYZ' in navbar config, Docusaurus
 * looks up the component here.
 */

import ComponentTypes from '@theme-original/NavbarItem/ComponentTypes';
import LoginLogoutNavbarItem from './LoginLogoutNavbarItem';

export default {
  ...ComponentTypes,
  'custom-LoginLogoutNavbarItem': LoginLogoutNavbarItem,
};
