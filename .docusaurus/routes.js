import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/blog',
    component: ComponentCreator('/blog', 'b2f'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive', '182'),
    exact: true
  },
  {
    path: '/blog/authors',
    component: ComponentCreator('/blog/authors', '0b7'),
    exact: true
  },
  {
    path: '/blog/authors/all-sebastien-lorber-articles',
    component: ComponentCreator('/blog/authors/all-sebastien-lorber-articles', '4a1'),
    exact: true
  },
  {
    path: '/blog/authors/yangshun',
    component: ComponentCreator('/blog/authors/yangshun', 'a68'),
    exact: true
  },
  {
    path: '/blog/first-blog-post',
    component: ComponentCreator('/blog/first-blog-post', '89a'),
    exact: true
  },
  {
    path: '/blog/long-blog-post',
    component: ComponentCreator('/blog/long-blog-post', '9ad'),
    exact: true
  },
  {
    path: '/blog/mdx-blog-post',
    component: ComponentCreator('/blog/mdx-blog-post', 'e9f'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags', '287'),
    exact: true
  },
  {
    path: '/blog/tags/docusaurus',
    component: ComponentCreator('/blog/tags/docusaurus', '704'),
    exact: true
  },
  {
    path: '/blog/tags/facebook',
    component: ComponentCreator('/blog/tags/facebook', '858'),
    exact: true
  },
  {
    path: '/blog/tags/hello',
    component: ComponentCreator('/blog/tags/hello', '299'),
    exact: true
  },
  {
    path: '/blog/tags/hola',
    component: ComponentCreator('/blog/tags/hola', '00d'),
    exact: true
  },
  {
    path: '/blog/welcome',
    component: ComponentCreator('/blog/welcome', 'd2b'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '5c0'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '235'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', 'a71'),
            routes: [
              {
                path: '/docs/assessments/ros2-project',
                component: ComponentCreator('/docs/assessments/ros2-project', 'f21'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/hardware/workstation-jetson',
                component: ComponentCreator('/docs/hardware/workstation-jetson', 'ffc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/introduction/',
                component: ComponentCreator('/docs/introduction/', 'aeb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/lab-setup/on-prem-cloud',
                component: ComponentCreator('/docs/lab-setup/on-prem-cloud', '7a4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-1-ros2/chapter-1-ros2-basics',
                component: ComponentCreator('/docs/module-1-ros2/chapter-1-ros2-basics', '0fb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-1-ros2/chapter-2-urdf-humanoids',
                component: ComponentCreator('/docs/module-1-ros2/chapter-2-urdf-humanoids', '541'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-2-digital-twin/chapter-1-physics-simulation',
                component: ComponentCreator('/docs/module-2-digital-twin/chapter-1-physics-simulation', '648'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-2-digital-twin/chapter-2-gazebo-unity-environments',
                component: ComponentCreator('/docs/module-2-digital-twin/chapter-2-gazebo-unity-environments', 'ba1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-3-isaac/chapter-1-isaac-sim',
                component: ComponentCreator('/docs/module-3-isaac/chapter-1-isaac-sim', 'f1c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-3-isaac/chapter-2-isaac-ros-navigation',
                component: ComponentCreator('/docs/module-3-isaac/chapter-2-isaac-ros-navigation', '322'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-4-vla/chapter-1-whisper-llms',
                component: ComponentCreator('/docs/module-4-vla/chapter-1-whisper-llms', '712'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-4-vla/chapter-2-capstone-pipeline',
                component: ComponentCreator('/docs/module-4-vla/chapter-2-capstone-pipeline', 'b9e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/weekly-breakdowns/week-1-overview',
                component: ComponentCreator('/docs/weekly-breakdowns/week-1-overview', 'b30'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
