/**
 * Navbar Item Component Types
 * Registers custom navbar items with Docusaurus
 */
import ComponentTypes from '@theme-original/NavbarItem/ComponentTypes';
import CustomLoginLogoutNavbarItem from './CustomLoginLogoutNavbarItem';

export default {
  ...ComponentTypes,
  'custom-LoginLogoutNavbarItem': CustomLoginLogoutNavbarItem,
};
