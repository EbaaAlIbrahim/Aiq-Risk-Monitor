import { ApplicationConfig } from '@angular/core';
import { provideHttpClient } from '@angular/common/http'; 

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient() // Simply provide the HTTP client features directly
  ]
};
