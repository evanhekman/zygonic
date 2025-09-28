import React from 'react';

export const GlobalStyles: React.FC = () => {
  return (
    <style jsx global>{`
        .range-slider {
            -webkit-appearance: none;
            appearance: none;
            height: 8px;
            border-radius: 4px;
            outline: none;
            background: transparent;
        }

        .range-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            height: 16px;
            width: 20px;
            border-radius: 50%;
            background: #06b6d4;
            cursor: pointer;
            border: 2px solid #0f172a;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            transition: all 0.15s ease;
        }

        .range-slider::-webkit-slider-thumb:hover {
            background: #0891b2;
            transform: scale(1.1);
        }

        .range-slider::-webkit-slider-thumb:active {
            transform: scale(0.95);
        }
    `}</style>
  );
};
