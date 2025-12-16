import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'A comprehensive guide to embodied intelligence and humanoid robotics',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://your-textbook-site.example.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'your-org', // Usually your GitHub org/user name.
  projectName: 'physical-ai-humanoid-robotics', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {to: '/blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/your-org/physical-ai-humanoid-robotics',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Introduction',
          items: [
            {
              label: 'Module 1 – The Robotic Nervous System (ROS 2)',
              to: '/docs/module-1-ros2',
            },
            {
              label: 'Chapter 1: ROS 2 Basics',
              to: '/docs/module-1-ros2/chapter-1-ros2-basics',
            },
            {
              label: 'Chapter 2: URDF Basics for Humanoids',
              to: '/docs/module-1-ros2/chapter-2-urdf-humanoids',
            },
            {
              label: 'Module 2 – The Digital Twin (Gazebo & Unity)',
              to: '/docs/module-2-digital-twin',
            },
            {
              label: 'Chapter 1: Physics Simulation',
              to: '/docs/module-2-digital-twin/chapter-1-physics-simulation',
            },
            {
              label: 'Chapter 2: Gazebo & Unity Environments',
              to: '/docs/module-2-digital-twin/chapter-2-gazebo-unity-environments',
            },
            {
              label: 'Module 3 – The AI-Robot Brain (NVIDIA Isaac)',
              to: '/docs/module-3-isaac',
            },
            {
              label: 'Chapter 1: Isaac Sim',
              to: '/docs/module-3-isaac/chapter-1-isaac-sim',
            },
            {
              label: 'Chapter 2: Isaac ROS Navigation',
              to: '/docs/module-3-isaac/chapter-2-isaac-ros-navigation',
            },
            {
              label: 'Module 4 – Vision-Language-Action (VLA)',
              to: '/docs/module-4-vla',
            },
            {
              label: 'Chapter 1: Whisper & LLMs',
              to: '/docs/module-4-vla/chapter-1-whisper-llms',
            },
            {
              label: 'Chapter 2: Full Capstone Pipeline',
              to: '/docs/module-4-vla/chapter-2-capstone-pipeline',
            },
            {
              label: 'Weekly Breakdown Chapters',
              to: '/docs/weekly-breakdowns',
            },
            {
              label: 'Assessment Chapters',
              to: '/docs/assessments',
            },
            {
              label: 'Hardware Chapters',
              to: '/docs/hardware',
            },
            {
              label: 'Cloud vs On-Premise Lab Setup',
              to: '/docs/lab-setup',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/your-org/physical-ai-humanoid-robotics',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,

  plugins: [
    // RAG Chatbot Plugin
    './frontend/plugins/rag-chatbot',
  ],
};

export default config;
