import React from 'react'
import  { PureResultTabs } from './ResultSection'
import { action } from '@storybook/addon-actions';

export default {
    component: PureResultTabs,
    title: 'Result tabs',
    decorators: [story => <div style={{ padding: '3rem'}}>{story()}</div>],
    excludeStories: /.*Data$/
};

export const countsData = {
    selectedType: "project",
    counts: {
        projects: 4,
        experiments: 14,
        datasets: 5,
        datafiles: 80
    },
    onChange: action("level change")
}

export const emptyCountsData = Object.assign({},countsData,
    {
        counts: null
    }
);

export const Default = () => (<PureResultTabs {...countsData} />);

export const EmptyCounts = () => (<PureResultTabs {...emptyCountsData} />);