'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { PropertyData, DistanceInfo } from '../types/property';
import { ChatMessage } from '../types/chat';

interface TabsContextType {
  // Property data
  propertyData: PropertyData | null;
  setPropertyData: (data: PropertyData | null) => void;
  
  // Distance information
  distanceInfo: DistanceInfo | null;
  setDistanceInfo: (info: DistanceInfo | null) => void;
  
  // Chat state
  messages: ChatMessage[];
  setMessages: (messages: ChatMessage[]) => void;
  isSending: boolean;
  setIsSending: (isSending: boolean) => void;
  
  // Active tab
  activeTab: 'property' | 'distance' | 'chat';
  setActiveTab: (tab: 'property' | 'distance' | 'chat') => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

export const TabsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [propertyData, setPropertyData] = useState<PropertyData | null>(null);
  const [distanceInfo, setDistanceInfo] = useState<DistanceInfo | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [activeTab, setActiveTab] = useState<'property' | 'distance' | 'chat'>('property');

  const value = {
    propertyData,
    setPropertyData,
    distanceInfo,
    setDistanceInfo,
    messages,
    setMessages,
    isSending,
    setIsSending,
    activeTab,
    setActiveTab,
  };

  return (
    <TabsContext.Provider value={value}>
      {children}
    </TabsContext.Provider>
  );
};

export const useTabs = () => {
  const context = useContext(TabsContext);
  if (context === undefined) {
    throw new Error('useTabs must be used within a TabsProvider');
  }
  return context;
}; 