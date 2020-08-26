import React from 'react';
import Tabs from "react-bootstrap/Tabs";
import Tab from 'react-bootstrap/Tab';
import { OBJECT_TYPE_STICKERS } from '../../TabStickers/TabSticker'
import TypeSchemaList from '../type-schema-list/TypeSchemaList';
import { useSelector } from "react-redux";
import TypeAttributesList from "../type-attributes-list/TypeAttributesList";

export default function FiltersSection() {
  const typeIds = useSelector((state) => (state.filters.types.allIds));
  const isLoading = useSelector((state) => (state.filters.isLoading));
  const error = useSelector((state) => (state.filters.error));

  if (isLoading) {
    return <p>Loading filters...</p>
  }
  if (error) {
    return <p>An error occurred while loading filters.</p>
  }

  return (
    <section>
      <h2 className="h3">Filters</h2>
      <Tabs defaultActiveKey="projects" id="filters-section">
        {
          typeIds.map(type => {
            const Sticker = OBJECT_TYPE_STICKERS[type];

            return (
              <Tab key={type} eventKey={type} title={<Sticker />}>
                <TypeAttributesList typeId={type} />
                <TypeSchemaList typeId={type} />
              </Tab>
            );
          })
        }
      </Tabs>
    </section>
  )
}