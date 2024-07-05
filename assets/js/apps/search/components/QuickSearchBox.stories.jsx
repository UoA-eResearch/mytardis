import React from 'react'
import { PureQuickSearchBox } from './QuickSearchBox';
// import { action } from '@storybook/addon-actions';
import { fn } from '@storybook/test';

export default {
  component: PureQuickSearchBox,
  title: 'Quick search box',
  decorators: [story => <div style={{ padding: '3rem' }}>{story()}</div>],
  excludeStories: /.*Data$/,
};

export const Default = () => (
  <PureQuickSearchBox
      searchTerm=""
      typeName="experiments"
      onSubmit={fn()}
      onChange={fn()} 
  />
);

export const Filled = () => (
  <PureQuickSearchBox
      searchTerm="A search term!"
      typeName="experiments"
      onSubmit={fn()}
      onChange={fn()} 
  />
);
